import json
import os
import shutil
import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXISTING_TEST_FILE_PATH = os.path.join(PROJECT_DIR, "pyproject.toml")

CONFIG_FILE_PATHS = {
    "actual": os.path.join(PROJECT_DIR, "config", "config.json"),
    "temporary": os.path.join(PROJECT_DIR, "config", "config.original.json"),
    "test_content": json.dumps(
        {
            "general": {
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
        },
        indent=4,
    ),
}
INFO_LOGS_PATHS = {
    "actual": os.path.join(PROJECT_DIR, "logs", "info.log"),
    "temporary": os.path.join(PROJECT_DIR, "logs", "info.original.log"),
    "test_content": "",
}
DEBUG_LOGS_PATHS = {
    "actual": os.path.join(PROJECT_DIR, "logs", "debug.log"),
    "temporary": os.path.join(PROJECT_DIR, "logs", "debug.original.log"),
    "test_content": "",
}


@pytest.fixture()
def original_config():
    # save original config.json for later
    assert not os.path.isfile(CONFIG_FILE_PATHS["temporary"])
    try:
        shutil.copyfile(CONFIG_FILE_PATHS["actual"], CONFIG_FILE_PATHS["temporary"])
    except FileNotFoundError:
        pass

    # create temporary file
    with open(CONFIG_FILE_PATHS["actual"], "w") as f:
        f.write(CONFIG_FILE_PATHS["test_content"])

    # run the respective test
    yield json.loads(CONFIG_FILE_PATHS["test_content"])

    # restore original config.json
    os.remove(CONFIG_FILE_PATHS["actual"])
    try:
        os.rename(CONFIG_FILE_PATHS["temporary"], CONFIG_FILE_PATHS["actual"])
    except FileNotFoundError:
        pass


@pytest.fixture()
def original_logs():
    assert not os.path.isfile(INFO_LOGS_PATHS["temporary"])
    assert not os.path.isfile(DEBUG_LOGS_PATHS["temporary"])

    # save original log files for later
    for ps in [INFO_LOGS_PATHS, DEBUG_LOGS_PATHS]:
        try:
            shutil.copyfile(ps["actual"], ps["temporary"])
        except FileNotFoundError:
            pass

        # create temporary file
        with open(ps["actual"], "w") as f:
            f.write(ps["test_content"])

    # run the respective test
    yield

    # restore original log files
    for ps in [INFO_LOGS_PATHS, DEBUG_LOGS_PATHS]:
        os.remove(ps["actual"])
        try:
            os.rename(ps["temporary"], ps["actual"])
        except FileNotFoundError:
            pass
