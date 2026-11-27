import time

import tum_esm_utils

from packages.core import types, utils

from .state_interface import StateInterface
from .state_interface import STATE_LOCK_PATH

_DEFAULT_EXCEPTION_PATIENCE_SECONDS = 300
_NOTIFICATION_LOCK_PATH = STATE_LOCK_PATH + ".notifications"
_NOTIFICATION_RETRY_SECONDS = 600
_notification_retry_at = 0.0


class ExceptionsInterface:
    """Interface for exceptions handling."""

    def __init__(
        self,
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> None:
        self.state_lock = state_lock
        self.logger = logger

    @staticmethod
    def _validate_exception_type(exception_type: types.KnownException) -> None:
        if not types.KNOWN_EXCEPTIONS.is_registered(exception_type):
            raise ValueError("exception_type must be a registered KNOWN_EXCEPTIONS entry")

    def add_exception(
        self,
        origin: str,
        exception_type: types.KnownException | Exception,
        traceback: str | None = None,
        details: str | None = None,
    ) -> None:
        """Record a catalog entry or caught error, unless the same fault is already active."""

        if isinstance(exception_type, types.CataloguedError):
            exception_type = exception_type.exception_type
        elif isinstance(exception_type, Exception):
            exception_type = types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR
        self._validate_exception_type(exception_type)
        with StateInterface.update_state(self.state_lock, self.logger) as state:
            is_active = any(
                item.origin == origin
                and item.exception_type == exception_type.identifier
                and item.cleared_at is None
                for item in state.exceptions_state.exceptions
            )
            if is_active:
                return

            state.exceptions_state.exceptions.append(
                types.ExceptionStateItem(
                    origin=origin,
                    exception_type=exception_type.identifier,
                    subject=exception_type.error_message,
                    description=exception_type.long_description,
                    traceback=traceback,
                    details=details,
                    raised_at=time.time(),
                )
            )

    def resolve_exception(
        self,
        origin: str,
        exception_type: types.KnownException | None = None,
        exclude_exception_types: list[types.KnownException] | None = None,
    ) -> None:
        """Mark matching active exceptions as cleared.

        If no exception type is provided, all active exceptions from the
        origin are resolved except explicitly excluded types.
        """

        if exception_type is not None:
            self._validate_exception_type(exception_type)
        excluded_exception_types = exclude_exception_types or []
        for excluded_exception_type in excluded_exception_types:
            self._validate_exception_type(excluded_exception_type)

        excluded_identifiers = {
            excluded_exception_type.identifier
            for excluded_exception_type in excluded_exception_types
        }
        cleared_at = time.time()
        with StateInterface.update_state(self.state_lock, self.logger) as state:
            for item in state.exceptions_state.exceptions:
                if (
                    item.origin == origin
                    and item.cleared_at is None
                    and (exception_type is None or item.exception_type == exception_type.identifier)
                    and item.exception_type not in excluded_identifiers
                ):
                    item.cleared_at = cleared_at

    @staticmethod
    def update_exception_notifications(
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
        config: types.Config,
    ) -> None:
        """Send due notifications, retry failed delivery after ten minutes, and clean up."""

        global _notification_retry_at
        now = time.time()
        patience_by_identifier = config.error_email.exception_patience.model_dump(by_alias=True)
        patience_by_identifier[types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR.identifier] = 0
        # Serialize core/CLI senders without blocking producers on the state lock.
        notification_lock = tum_esm_utils.sqlitelock.SQLiteLock(
            filepath=_NOTIFICATION_LOCK_PATH, timeout=0
        )
        try:
            notification_lock.acquire()
        except TimeoutError:
            logger.debug("Another process is updating exception notifications")
            return

        try:
            state = StateInterface.load_state(state_lock, logger)
            exception_state = state.exceptions_state
            active_exceptions = [
                item for item in exception_state.exceptions if item.cleared_at is None
            ]
            email_enabled_exceptions = [
                item
                for item in active_exceptions
                if patience_by_identifier.get(
                    item.exception_type, _DEFAULT_EXCEPTION_PATIENCE_SECONDS
                )
                != -1
            ]
            due_exceptions = [
                item
                for item in email_enabled_exceptions
                if item.notified_at is None
                and (now - item.raised_at)
                >= patience_by_identifier.get(
                    item.exception_type, _DEFAULT_EXCEPTION_PATIENCE_SECONDS
                )
            ]

            can_send = (
                not config.general.test_mode
                and config.error_email.notify_recipients
                and time.monotonic() >= _notification_retry_at
            )
            if can_send:
                try:
                    if due_exceptions:
                        utils.ExceptionEmailClient.handle_occured_exceptions(config, due_exceptions)
                    elif not email_enabled_exceptions and exception_state.notification_sent:
                        utils.ExceptionEmailClient.handle_resolved_exception(config)
                except Exception as e:
                    _notification_retry_at = time.monotonic() + _NOTIFICATION_RETRY_SECONDS
                    can_send = False
                    logger.exception(e)
                    logger.error("Email delivery failed; retrying notifications in 10 minutes")

            # Reload so faults raised or resolved during SMTP are preserved.
            with StateInterface.update_state(state_lock, logger) as state:
                if due_exceptions and can_send:
                    sent_occurrences = {
                        (item.origin, item.exception_type, item.raised_at)
                        for item in due_exceptions
                    }
                    for item in state.exceptions_state.exceptions:
                        if (item.origin, item.exception_type, item.raised_at) in sent_occurrences:
                            item.notified_at = now
                    state.exceptions_state.notification_sent = True
                if (
                    not config.general.test_mode
                    and not email_enabled_exceptions
                    and (can_send or not config.error_email.notify_recipients)
                ):
                    state.exceptions_state.notification_sent = False
                state.exceptions_state.exceptions = [
                    item for item in state.exceptions_state.exceptions if item.cleared_at is None
                ]
        finally:
            notification_lock.release()
