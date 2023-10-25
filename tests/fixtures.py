import json
import os
from typing import Any
import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXISTING_TEST_FILE_PATH = os.path.join(PROJECT_DIR, "pyproject.toml")

SAMPLE_CONFIG = {
    "general": {
        "version": "4.0.8",
        "seconds_per_core_interval": 30,
        "test_mode": True,
        "station_id": "...",
        "min_sun_elevation": 11,
    },
    "opus": {
        "em27_ip": "10.10.0.1",
        "executable_path": EXISTING_TEST_FILE_PATH,
        "experiment_path": EXISTING_TEST_FILE_PATH,
        "macro_path": EXISTING_TEST_FILE_PATH,
        "username": "Default",
        "password": "...",
    },
    "camtracker": {
        "config_path": EXISTING_TEST_FILE_PATH,
        "executable_path": EXISTING_TEST_FILE_PATH,
        "learn_az_elev_path": EXISTING_TEST_FILE_PATH,
        "sun_intensity_path": EXISTING_TEST_FILE_PATH,
        "motor_offset_threshold": 10,
    },
    "error_email": {
        "sender_address": "pyra.technical.user@gmail.com",
        "sender_password": "...",
        "notify_recipients": True,
        "recipients": "your@mail.com",
    },
    "measurement_decision": {
        "mode": "automatic",
        "manual_decision_result": False,
        "cli_decision_result": False,
    },
    "measurement_triggers": {
        "consider_time": True,
        "consider_sun_elevation": True,
        "consider_helios": False,
        "start_time": {"hour": 7, "minute": 0, "second": 0},
        "stop_time": {"hour": 21, "minute": 0, "second": 0},
        "min_sun_elevation": 0,
    },
    "tum_plc": None,
    "helios": None,
    "upload": None,
}


def save_file(
    original_path: str, temporary_path: str, test_content: str
) -> None:
    assert not os.path.exists(temporary_path)

    try:
        os.rename(original_path, temporary_path)
    except FileNotFoundError:
        pass

    with open(original_path, "w") as f:
        f.write(test_content)


def restore_file(original_path: str, temporary_path: str) -> None:
    os.remove(original_path)
    try:
        os.rename(temporary_path, original_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def sample_config() -> Any:
    """
    Store the original config.json file under a different name.
    Restore it after the tests are done.

    Yields a sample config.
    """

    original_config_path = os.path.join(PROJECT_DIR, "config", "config.json")
    temporary_config_path = os.path.join(
        PROJECT_DIR, "config", "config.tmp.json"
    )
    config_string = json.dumps(SAMPLE_CONFIG, indent=4)
    save_file(original_config_path, temporary_config_path, config_string)

    # run the respective test
    yield SAMPLE_CONFIG

    restore_file(original_config_path, temporary_config_path)


@pytest.fixture()
def original_config() -> Any:
    """
    Store the original config.json file under a different name.
    Restore it after the tests are done.

    Yields the original config (from config.json).
    """

    original_config_path = os.path.join(PROJECT_DIR, "config", "config.json")
    temporary_config_path = os.path.join(
        PROJECT_DIR, "config", "config.tmp.json"
    )

    assert os.path.isfile(original_config_path)
    with open(original_config_path) as f:
        config_string = f.read()
    save_file(original_config_path, temporary_config_path, config_string)

    # run the respective test
    yield json.loads(config_string)

    restore_file(original_config_path, temporary_config_path)


@pytest.fixture()
def empty_logs() -> Any:
    """
    Store the original info.log and debug.log file under a
    different name. Restore them after the tests are done.

    Yields nothing, but the log files are emtpy.
    """
    original_info_logs_path = os.path.join(PROJECT_DIR, "logs", "info.log")
    temporary_info_logs_path = os.path.join(PROJECT_DIR, "logs", "info.tmp.log")
    save_file(original_info_logs_path, temporary_info_logs_path, "")

    original_debug_logs_path = os.path.join(PROJECT_DIR, "logs", "debug.log")
    temporary_debug_logs_path = os.path.join(
        PROJECT_DIR, "logs", "debug.tmp.log"
    )
    save_file(original_debug_logs_path, temporary_debug_logs_path, "")

    # run the respective test
    yield

    restore_file(original_info_logs_path, temporary_info_logs_path)
    restore_file(original_debug_logs_path, temporary_debug_logs_path)
