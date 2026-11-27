import threading
from pathlib import Path
from unittest.mock import Mock

import pytest
import tum_esm_utils

from packages.core import interfaces, types, utils
from packages.core.interfaces import exceptions_interface, state_interface
from tests.fixtures import SAMPLE_CONFIG


@pytest.mark.ci
def test_exception_catalog_identifiers_are_unique() -> None:
    """Prevent catalog entries from sharing the identifier used to persist faults."""
    identifiers = [entry.identifier for entry in types.KNOWN_EXCEPTIONS.all()]
    assert len(identifiers) == len(set(identifiers))


@pytest.fixture()
def exception_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger]:
    state_path = str(tmp_path / "state.json")
    monkeypatch.setattr(state_interface, "_STATE_FILE_PATH", state_path)
    monkeypatch.setattr(exceptions_interface, "_notification_retry_at", 0.0)
    monkeypatch.setattr(
        exceptions_interface, "_NOTIFICATION_LOCK_PATH", str(tmp_path / "notifications.sqlitelock")
    )
    logger = utils.Logger(origin="test", lock=threading.Lock(), just_print=True)
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=str(tmp_path / "state.sqlitelock"),
        timeout=1,
        poll_interval=0.01,
    )
    return interfaces.ExceptionsInterface(state_lock, logger), state_lock, logger


@pytest.mark.ci
def test_add_resolve_and_reraise_exception(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persist fault details once while active, but record a new occurrence after resolution."""
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])

    exception_type = types.KNOWN_EXCEPTIONS.HELIOS_CAMERA_ERROR
    exception_interface.add_exception(
        "helios", exception_type, traceback="traceback", details="details"
    )
    now[0] = 1000.5
    exception_interface.add_exception("helios", exception_type)

    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert len(state.exceptions_state.exceptions) == 1
    item = state.exceptions_state.exceptions[0]
    assert item.exception_type == exception_type.identifier
    assert item.subject == exception_type.error_message
    assert item.description == exception_type.long_description
    assert item.traceback == "traceback"
    assert item.details == "details"
    assert item.raised_at == 1000.0

    now[0] = 1001.0
    exception_interface.resolve_exception("helios", exception_type)
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].cleared_at == 1001.0

    now[0] = 1002.0
    exception_interface.add_exception("helios", exception_type)
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert len(state.exceptions_state.exceptions) == 2
    assert state.exceptions_state.exceptions[1].raised_at == 1002.0


@pytest.mark.parametrize(
    "error, expected",
    [
        (types.HeliosCameraError("camera unavailable"), types.KNOWN_EXCEPTIONS.HELIOS_CAMERA_ERROR),
        (RuntimeError("unknown failure"), types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR),
    ],
)
@pytest.mark.ci
def test_add_caught_exception(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    error: Exception,
    expected: types.KnownException,
) -> None:
    """Caught catalogued errors and unknown errors must take different reporting paths."""

    exception_interface, state_lock, logger = exception_store
    exception_interface.add_exception("test", error)

    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert len(state.exceptions_state.exceptions) == 1
    item = state.exceptions_state.exceptions[0]
    assert item.exception_type == expected.identifier


@pytest.mark.ci
def test_resolve_all_with_excluded_exception_types(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve only the requested origin while preserving explicitly excluded faults."""
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])

    storage_error = types.KNOWN_EXCEPTIONS.STORAGE_ERROR
    low_energy_error = types.KNOWN_EXCEPTIONS.LOW_ENERGY_ERROR
    unexpected_error = types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR
    exception_interface.add_exception("system-monitor", storage_error)
    exception_interface.add_exception("system-monitor", low_energy_error)
    exception_interface.add_exception("another-origin", unexpected_error)

    now[0] = 1001.0
    exception_interface.resolve_exception(
        "system-monitor", exclude_exception_types=[low_energy_error]
    )
    state = interfaces.StateInterface.load_state(state_lock, logger)
    items_by_identifier = {item.exception_type: item for item in state.exceptions_state.exceptions}
    assert items_by_identifier[storage_error.identifier].cleared_at == 1001.0
    assert items_by_identifier[low_energy_error.identifier].cleared_at is None
    assert items_by_identifier[unexpected_error.identifier].cleared_at is None

    now[0] = 1002.0
    exception_interface.resolve_exception("system-monitor")
    state = interfaces.StateInterface.load_state(state_lock, logger)
    items_by_identifier = {item.exception_type: item for item in state.exceptions_state.exceptions}
    assert items_by_identifier[low_energy_error.identifier].cleared_at == 1002.0
    assert items_by_identifier[unexpected_error.identifier].cleared_at is None


@pytest.mark.ci
def test_rejects_unregistered_exception(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
) -> None:
    """Keep uncatalogued exception types out of both additions and resolution requests."""
    exception_interface, _, _ = exception_store
    unregistered = types.KnownException(
        identifier="unregistered",
        error_message="Unregistered",
        long_description="Not part of the catalog.",
    )

    with pytest.raises(ValueError):
        exception_interface.add_exception("test", unregistered)

    class UnregisteredError(types.CataloguedError):
        exception_type = unregistered

    with pytest.raises(ValueError):
        exception_interface.add_exception("test", UnregisteredError())
    with pytest.raises(ValueError):
        exception_interface.resolve_exception("test", unregistered)
    with pytest.raises(ValueError):
        exception_interface.resolve_exception("test", exclude_exception_types=[unregistered])


@pytest.mark.ci
def test_notification_delay_and_staggered_resolution(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prevent early alerts and premature recovery emails: notify at the exact patience
    boundary, then send recovery only after the remaining exception clears.
    """
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])

    occurred, resolved = Mock(), Mock()
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_resolved_exception", resolved)
    config = SAMPLE_CONFIG.model_copy(deep=True)

    first = types.KNOWN_EXCEPTIONS.STORAGE_ERROR
    second = types.KNOWN_EXCEPTIONS.LOW_ENERGY_ERROR
    exception_interface.add_exception("system-monitor", first)

    now[0] = 1299.9
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    occurred.assert_not_called()

    now[0] = 1300.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    occurred.assert_called_once()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].notified_at == 1300.0
    assert state.exceptions_state.notification_sent

    exception_interface.add_exception("system-monitor", second)
    exception_interface.resolve_exception("system-monitor", first)
    now[0] = 1301.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    resolved.assert_not_called()

    exception_interface.resolve_exception("system-monitor", second)
    now[0] = 1302.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    resolved.assert_called_once_with(config)
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions == []
    assert not state.exceptions_state.notification_sent


@pytest.mark.ci
def test_resolved_before_patience_sends_no_email(
    exception_store: tuple[
        interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A fault that recovers or is no longer required before its delay must disappear without emails."""
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    occurred, resolved = Mock(), Mock()
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_resolved_exception", resolved)
    config = SAMPLE_CONFIG.model_copy(deep=True)

    exception_interface.add_exception("helios", types.KNOWN_EXCEPTIONS.HELIOS_CAMERA_ERROR)
    now[0] = 1001.0
    exception_interface.resolve_exception("helios")
    now[0] = 1600.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)

    occurred.assert_not_called()
    resolved.assert_not_called()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions == []
    assert not state.exceptions_state.notification_sent


@pytest.mark.parametrize("recovery", [False, True])
@pytest.mark.ci
def test_failed_notification_retries_every_ten_minutes(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
    recovery: bool,
) -> None:
    """Delivery failures must not escape, and both email types retry at a fixed ten-minute interval."""
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    monkeypatch.setattr(exceptions_interface.time, "monotonic", lambda: now[0])
    exception_interface.add_exception("test", types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR)
    if recovery:
        exception_interface.resolve_exception("test")
        with interfaces.StateInterface.update_state(state_lock, logger) as state:
            state.exceptions_state.notification_sent = True
    delivery = Mock(side_effect=RuntimeError("SMTP failed"))
    monkeypatch.setattr(
        utils.ExceptionEmailClient,
        "handle_resolved_exception" if recovery else "handle_occured_exceptions",
        delivery,
    )
    config = SAMPLE_CONFIG.model_copy(deep=True)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.notification_sent == recovery
    if not recovery:
        assert state.exceptions_state.exceptions[0].notified_at is None

    now[0] = 1599.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    delivery.assert_called_once()
    now[0] = 1600.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert delivery.call_count == 2
    delivery.side_effect = None
    now[0] = 2199.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert delivery.call_count == 2
    now[0] = 2200.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert delivery.call_count == 3
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.notification_sent == (not recovery)
    if not recovery:
        assert state.exceptions_state.exceptions[0].notified_at == 2200.0


@pytest.mark.ci
def test_occurrence_delivery_preserves_concurrent_producer_updates(
    exception_store: tuple[
        interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SMTP must release the state lock, preserve new occurrences, and exclude another sender."""
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    config = SAMPLE_CONFIG.model_copy(deep=True)
    error = types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR
    exception_interface.add_exception("test", error)

    def deliver(config: types.Config, items: list[types.ExceptionStateItem]) -> None:
        assert not state_lock.is_locked()
        # A competing notifier must skip delivery while this sender is active.
        interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
        exception_interface.resolve_exception("test", error)
        now[0] += 1
        exception_interface.add_exception("test", error)

    occurred = Mock(side_effect=deliver)
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)

    occurred.assert_called_once()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    (item,) = state.exceptions_state.exceptions
    assert item.raised_at == 1001.0
    assert item.notified_at is None
    assert item.cleared_at is None
    assert state.exceptions_state.notification_sent


@pytest.mark.ci
def test_recovery_delivery_preserves_new_faults(
    exception_store: tuple[
        interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recovery delivery must also release the state lock and retain faults raised during SMTP."""
    exception_interface, state_lock, logger = exception_store
    config = SAMPLE_CONFIG.model_copy(deep=True)
    with interfaces.StateInterface.update_state(state_lock, logger) as state:
        state.exceptions_state.notification_sent = True

    def deliver(config: types.Config) -> None:
        assert not state_lock.is_locked()
        exception_interface.add_exception("test", types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR)

    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_resolved_exception", deliver)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)

    state = interfaces.StateInterface.load_state(state_lock, logger)
    (item,) = state.exceptions_state.exceptions
    assert item.notified_at is None
    assert item.cleared_at is None
    assert not state.exceptions_state.notification_sent


@pytest.mark.ci
def test_disabled_notification_is_not_marked_as_sent(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The global email switch must suppress delivery and leave faults unnotified."""
    exception_interface, state_lock, logger = exception_store
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: 1000.0)
    exception_interface.add_exception("test", types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR)
    occurred = Mock()
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)

    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.error_email.notify_recipients = False
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)

    occurred.assert_not_called()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].notified_at is None
    assert not state.exceptions_state.notification_sent


@pytest.mark.ci
def test_independent_patience_and_unconfigurable_exception(
    exception_store: tuple[
        interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prevent one delay from applying to every fault: check per-type defaults and
    overrides, immediate unexpected errors, the 300s fallback, and no repeat emails.
    """
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    occurred = Mock()
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)
    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.error_email.exception_patience.opus_connection_error = 600
    unconfigurable = types.KnownException(
        identifier="new-error",
        error_message="New error",
        long_description="New error",
        default_patience=0,
    )
    monkeypatch.setattr(types.KNOWN_EXCEPTIONS, "NEW_ERROR", unconfigurable, raising=False)
    for entry in [
        types.KNOWN_EXCEPTIONS.TUM_ENCLOSURE_RAIN_DETECTED_COVER_NOT_CLOSED,
        types.KNOWN_EXCEPTIONS.COVER_DID_NOT_CLOSE,
        types.KNOWN_EXCEPTIONS.OPUS_CONNECTION_ERROR,
        types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR,
        unconfigurable,
    ]:
        exception_interface.add_exception("test", entry)
    for age, expected_identifiers in [
        (0, ["tum-enclosure-rain-detected-cover-not-closed", "unexpected-error"]),
        (90, ["cover-did-not-close"]),
        (300, ["new-error"]),
        (600, ["opus-connection-error"]),
    ]:
        now[0] = 1000 + age
        interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
        occurred.assert_called_once()
        assert [item.exception_type for item in occurred.call_args.args[1]] == expected_identifiers
        occurred.reset_mock()
        interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
        occurred.assert_not_called()


@pytest.mark.ci
def test_muted_exceptions_persist_without_blocking_recovery(
    exception_store: tuple[
        interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep muted faults visible without blocking recovery: verify persistence without
    emails, one recovery after enabled faults clear, and cleanup when muted faults clear.
    """
    exception_interface, state_lock, logger = exception_store
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: 1000.0)
    occurred, resolved = Mock(), Mock()
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_resolved_exception", resolved)
    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.error_email.exception_patience.storage_error = -1
    config.error_email.exception_patience.low_energy_error = 0
    muted = types.KNOWN_EXCEPTIONS.STORAGE_ERROR
    enabled = types.KNOWN_EXCEPTIONS.LOW_ENERGY_ERROR

    exception_interface.add_exception("test", muted)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    occurred.assert_not_called()
    resolved.assert_not_called()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert len(state.exceptions_state.exceptions) == 1
    assert state.exceptions_state.exceptions[0].notified_at is None

    exception_interface.add_exception("test", enabled)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    occurred.assert_called_once()
    exception_interface.resolve_exception("test", enabled)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    resolved.assert_called_once()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert len(state.exceptions_state.exceptions) == 1
    assert state.exceptions_state.exceptions[0].exception_type == muted.identifier
    assert state.exceptions_state.exceptions[0].notified_at is None
    assert not state.exceptions_state.notification_sent

    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    resolved.assert_called_once()
    exception_interface.resolve_exception("test", muted)
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert (
        interfaces.StateInterface.load_state(state_lock, logger).exceptions_state.exceptions == []
    )
    resolved.assert_called_once()


@pytest.mark.ci
def test_live_patience_changes_preserve_fault_age(
    exception_store: tuple[
        interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Changing patience must use the original fault age rather than restarting its timer."""
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    occurred = Mock()
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", occurred)
    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.error_email.exception_patience.storage_error = 601
    exception_interface.add_exception("test", types.KNOWN_EXCEPTIONS.STORAGE_ERROR)

    now[0] = 1600.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    occurred.assert_not_called()
    config.error_email.exception_patience.storage_error = 600
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    occurred.assert_called_once()
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].raised_at == 1000
    assert state.exceptions_state.exceptions[0].notified_at == 1600
