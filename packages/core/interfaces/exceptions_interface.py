import time

import tum_esm_utils

from packages.core import types, utils

from .state_interface import StateInterface

_NOTIFICATION_DELAY_SECONDS = 300


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
        exception_type: types.KnownException,
        traceback: str | None = None,
        details: str | None = None,
    ) -> None:
        """Add a catalogued exception unless the same exception is already active."""

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
                    and (
                        exception_type is None
                        or item.exception_type == exception_type.identifier
                    )
                    and item.exception_type not in excluded_identifiers
                ):
                    item.cleared_at = cleared_at

    @staticmethod
    def update_exception_notifications(
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
        config: types.Config,
    ) -> None:
        """Send due notifications and remove cleared exception records."""

        now = time.time()
        with StateInterface.update_state(state_lock, logger) as state:
            exception_state = state.exceptions_state
            had_exceptions = len(exception_state.exceptions) > 0
            active_exceptions = [
                item for item in exception_state.exceptions if item.cleared_at is None
            ]
            due_exceptions = [
                item
                for item in active_exceptions
                if item.notified_at is None and (now - item.raised_at) > _NOTIFICATION_DELAY_SECONDS
            ]

            if due_exceptions and config.error_email.notify_recipients:
                utils.ExceptionEmailClient.handle_occured_exceptions(config, due_exceptions)
                for item in due_exceptions:
                    item.notified_at = now
                exception_state.notification_sent = True

            if had_exceptions and not active_exceptions:
                if exception_state.notification_sent and config.error_email.notify_recipients:
                    utils.ExceptionEmailClient.handle_resolved_exception(config)
                exception_state.notification_sent = False

            exception_state.exceptions = active_exceptions
