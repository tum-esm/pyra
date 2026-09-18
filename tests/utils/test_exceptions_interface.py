import datetime
import json
import threading
from pathlib import Path
from typing import Generator

import pytest
import tum_esm_utils

from packages.core import interfaces, types, utils
from packages.core.interfaces import exceptions_interface, state_interface
from tests.fixtures import SAMPLE_CONFIG


@pytest.mark.ci
def test_exception_catalog_identifiers_are_unique() -> None:
    identifiers = [entry.identifier for entry in types.KNOWN_EXCEPTIONS.all()]
    assert len(identifiers) == len(set(identifiers))


@pytest.fixture()
def exception_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[
    tuple[interfaces.ExceptionsInterface, tum_esm_utils.sqlitelock.SQLiteLock, utils.Logger],
    None,
    None,
]:
    state_path = str(tmp_path / "state.json")
    monkeypatch.setattr(state_interface, "_STATE_FILE_PATH", state_path)
    logger = utils.Logger(origin="test", lock=threading.Lock(), just_print=True)
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=str(tmp_path / "state.sqlitelock"),
        timeout=1,
        poll_interval=0.01,
    )
    yield interfaces.ExceptionsInterface(state_lock, logger), state_lock, logger


def test_add_resolve_and_reraise_exception(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])

    exception_type = types.KNOWN_EXCEPTIONS.HELIOS_CAMERA_ERROR
    exception_interface.add_exception(
        "helios", exception_type, traceback="traceback", details="details"
    )
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


def test_resolve_all_with_excluded_exception_types(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    items_by_identifier = {
        item.exception_type: item for item in state.exceptions_state.exceptions
    }
    assert items_by_identifier[storage_error.identifier].cleared_at == 1001.0
    assert items_by_identifier[low_energy_error.identifier].cleared_at is None
    assert items_by_identifier[unexpected_error.identifier].cleared_at is None

    now[0] = 1002.0
    exception_interface.resolve_exception("system-monitor")
    state = interfaces.StateInterface.load_state(state_lock, logger)
    items_by_identifier = {
        item.exception_type: item for item in state.exceptions_state.exceptions
    }
    assert items_by_identifier[low_energy_error.identifier].cleared_at == 1002.0
    assert items_by_identifier[unexpected_error.identifier].cleared_at is None


def test_rejects_unregistered_exception(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
) -> None:
    exception_interface, _, _ = exception_store
    unregistered = types.KnownException(
        identifier="unregistered",
        error_message="Unregistered",
        long_description="Not part of the catalog.",
    )

    with pytest.raises(ValueError):
        exception_interface.add_exception("test", unregistered)
    with pytest.raises(ValueError):
        exception_interface.resolve_exception(
            "test", exclude_exception_types=[unregistered]
        )


def test_notification_delay_and_staggered_resolution(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])

    occurred: list[list[types.ExceptionStateItem]] = []
    resolved: list[bool] = []

    def handle_occurred(config: types.Config, items: list[types.ExceptionStateItem]) -> None:
        occurred.append(items)

    def handle_resolved(config: types.Config) -> None:
        resolved.append(True)

    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", handle_occurred)
    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_resolved_exception", handle_resolved)
    config = SAMPLE_CONFIG.model_copy(deep=True)

    first = types.KNOWN_EXCEPTIONS.STORAGE_ERROR
    second = types.KNOWN_EXCEPTIONS.LOW_ENERGY_ERROR
    exception_interface.add_exception("system-monitor", first)

    now[0] = 1300.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert occurred == []

    now[0] = 1300.1
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert len(occurred) == 1
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].notified_at == 1300.1
    assert state.exceptions_state.notification_sent

    exception_interface.add_exception("system-monitor", second)
    exception_interface.resolve_exception("system-monitor", first)
    now[0] = 1301.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert resolved == []

    exception_interface.resolve_exception("system-monitor", second)
    now[0] = 1302.0
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)
    assert resolved == [True]
    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions == []
    assert not state.exceptions_state.notification_sent


def test_failed_notification_remains_retryable(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    exception_interface.add_exception("test", types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR)
    now[0] = 1301.0

    def fail(config: types.Config, items: list[types.ExceptionStateItem]) -> None:
        raise RuntimeError("SMTP failed")

    monkeypatch.setattr(utils.ExceptionEmailClient, "handle_occured_exceptions", fail)
    config = SAMPLE_CONFIG.model_copy(deep=True)
    with pytest.raises(RuntimeError, match="SMTP failed"):
        interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)

    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].notified_at is None
    assert not state.exceptions_state.notification_sent


def test_disabled_notification_is_not_marked_as_sent(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exception_interface, state_lock, logger = exception_store
    now = [1000.0]
    monkeypatch.setattr(exceptions_interface.time, "time", lambda: now[0])
    exception_interface.add_exception("test", types.KNOWN_EXCEPTIONS.UNEXPECTED_ERROR)
    now[0] = 1301.0

    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.error_email.notify_recipients = False
    interfaces.ExceptionsInterface.update_exception_notifications(state_lock, logger, config)

    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.exceptions_state.exceptions[0].notified_at is None
    assert not state.exceptions_state.notification_sent


def test_legacy_exception_state_resets_entire_state(
    exception_store: tuple[
        interfaces.ExceptionsInterface,
        tum_esm_utils.sqlitelock.SQLiteLock,
        utils.Logger,
    ],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _, state_lock, logger = exception_store
    legacy_state = types.StateObject(
        last_updated=datetime.datetime.now(),
        measurements_should_be_running=True,
    ).model_dump(mode="json")
    legacy_state["exceptions_state"] = {"current": [], "notified": []}
    state_path = str(tmp_path / "legacy-state.json")
    tum_esm_utils.files.dump_file(state_path, json.dumps(legacy_state))
    monkeypatch.setattr(state_interface, "_STATE_FILE_PATH", state_path)

    state = interfaces.StateInterface.load_state(state_lock, logger)
    assert state.measurements_should_be_running is None
    assert state.exceptions_state.exceptions == []
