import datetime
import threading
from unittest.mock import Mock

import pytest

from packages.core.threads import camtracker_thread
from tests.fixtures import SAMPLE_CONFIG


@pytest.mark.ci
def test_restarts_already_running_camtracker_when_offset_exceeds_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.general.test_mode = False
    config.camtracker.restart_if_logs_are_too_old = False
    monkeypatch.setattr(camtracker_thread.types.Config, "load", Mock(return_value=config))
    monkeypatch.setattr(camtracker_thread.utils, "Logger", Mock())
    monkeypatch.setattr(camtracker_thread.tum_esm_utils.sqlitelock, "SQLiteLock", Mock())
    monkeypatch.setattr(camtracker_thread.interfaces, "ExceptionsInterface", Mock())
    monkeypatch.setattr(
        camtracker_thread.interfaces.StateInterface,
        "load_state",
        Mock(
            return_value=Mock(measurements_should_be_running=True, last_bad_weather_detection=None)
        ),
    )

    program = camtracker_thread.CamTrackerProgram
    monkeypatch.setattr(program, "is_running", Mock(side_effect=[True, False]))
    position = Mock(dt=datetime.datetime.now(), azimuth_offset=-75.0, elevation_offset=-0.5)
    read_position = Mock(return_value=position)
    monkeypatch.setattr(program, "read_tracker_position", read_position)
    stop = Mock()
    start = Mock()
    monkeypatch.setattr(program, "stop", stop)
    monkeypatch.setattr(program, "start", start)

    clock = Mock()
    clock.time.return_value = 0.0

    def finish_thread(_seconds: float) -> None:
        clock.time.return_value = 43201.0

    monkeypatch.setattr(camtracker_thread, "time", clock)
    clock.sleep.side_effect = finish_thread

    camtracker_thread.CamTrackerThread.main(threading.Lock(), headless=True)

    stop.assert_called_once()
    start.assert_called_once()
    read_position.assert_called_once_with(config)
