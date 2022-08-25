import json
import os
import random
import shutil
import pytest
import fabric.connection

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXISTING_TEST_FILE_PATH = os.path.join(PROJECT_DIR, "pyproject.toml")

SAMPLE_CONFIG = {
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
}


def save_file(original_path: str, temporary_path: str, test_content: str) -> None:
    assert not os.path.exists(temporary_path)

    try:
        os.rename(original_path, temporary_path)
    except FileNotFoundError:
        pass

    with open(original_path, "w") as f:
        f.write(test_content)


def restore_file(original_path: str, temporary_path: str):
    os.remove(original_path)
    try:
        os.rename(temporary_path, original_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def sample_config():
    """
    Store the original config.json file under a different name.
    Restore it after the tests are done.

    Yields a sample config.
    """

    original_config_path = os.path.join(PROJECT_DIR, "config", "config.json")
    temporary_config_path = os.path.join(PROJECT_DIR, "config", "config.tmp.json")
    config_string = json.dumps(SAMPLE_CONFIG, indent=4)
    save_file(original_config_path, temporary_config_path, config_string)

    # run the respective test
    yield SAMPLE_CONFIG

    restore_file(original_config_path, temporary_config_path)


@pytest.fixture()
def original_config():
    """
    Store the original config.json file under a different name.
    Restore it after the tests are done.

    Yields the original config (from config.json).
    """

    original_config_path = os.path.join(PROJECT_DIR, "config", "config.json")
    temporary_config_path = os.path.join(PROJECT_DIR, "config", "config.tmp.json")

    assert os.path.isfile(original_config_path)
    with open(original_config_path) as f:
        config_string = f.read()
    save_file(original_config_path, temporary_config_path, config_string)

    # run the respective test
    yield json.loads(config_string)

    restore_file(original_config_path, temporary_config_path)


@pytest.fixture()
def empty_logs():
    """
    Store the original info.log and debug.log file under a
    different name. Restore them after the tests are done.

    Yields nothing, but the log files are emtpy.
    """
    original_info_logs_path = os.path.join(PROJECT_DIR, "logs", "info.log")
    temporary_info_logs_path = os.path.join(PROJECT_DIR, "logs", "info.tmp.log")
    save_file(original_info_logs_path, temporary_info_logs_path, "")

    original_debug_logs_path = os.path.join(PROJECT_DIR, "logs", "debug.log")
    temporary_debug_logs_path = os.path.join(PROJECT_DIR, "logs", "debug.tmp.log")
    save_file(original_debug_logs_path, temporary_debug_logs_path, "")

    # run the respective test
    yield

    restore_file(original_info_logs_path, temporary_info_logs_path)
    restore_file(original_debug_logs_path, temporary_debug_logs_path)


@pytest.fixture
def populated_upload_test_directories():
    """
    Store the content of the logs/helios directory under a
    different name
    """
    original_helios_dir = os.path.join(PROJECT_DIR, "logs", "helios")
    temporary_helios_dir = os.path.join(PROJECT_DIR, "logs", "helios-tmp")
    assert not os.path.exists(temporary_helios_dir)

    # replace original helios dir with empty test dir
    os.rename(original_helios_dir, temporary_helios_dir)
    os.mkdir(original_helios_dir)

    # add a second test dir (ifg upload)
    test_ifg_dir = os.path.join(PROJECT_DIR, "test-tmp")
    assert not os.path.exists(test_ifg_dir)
    os.mkdir(test_ifg_dir)

    # add a bunch of random sample files to these directories

    ifg_dates = popuplate_upload_test_directory(test_ifg_dir)
    helios_dates = popuplate_upload_test_directory(original_helios_dir)

    # run the respective test
    yield {"ifg_dates": ifg_dates, "helios_dates": helios_dates}

    # fill helios dir with original content again
    shutil.rmtree(original_helios_dir)
    os.rename(temporary_helios_dir, original_helios_dir)
    shutil.rmtree(test_ifg_dir)


def random_string() -> str:
    letters = [chr(i) for i in range(ord("a"), ord("z") + 1)]
    return "".join([random.choice(letters) for i in range(5)])


def popuplate_upload_test_directory(dir_path: str) -> list[str]:
    """
    Generates 5 directories with random dates (YYYYMMDD)
    each containing 10 files with random names
    """
    try:
        date_strings = []
        for _ in range(5):
            year = random.randint(2000, 2021)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_string = f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"
            date_strings.append(date_string)
            os.mkdir(os.path.join(dir_path, date_string))
            filenames = []
            for _ in range(10):
                filename = f"{random_string()}{date_string}{random_string()}"
                filenames.append(filename)
                with open(os.path.join(dir_path, date_string, filename), "w") as f:
                    f.write(random_string())
            with open(os.path.join(dir_path, date_string, "upload-meta.json"), "w") as f:
                json.dump(
                    {
                        "complete": False,
                        "fileList": filenames,
                        "createdTime": 0,
                        "lastModifiedTime": 0,
                    },
                    f,
                )

        return date_strings

    except FileExistsError:
        # this happens when the random functions produce
        # the same date or string twice
        shutil.rmtree(dir_path)
        os.mkdir(dir_path)
        return popuplate_upload_test_directory(dir_path)


@pytest.fixture
def fabric_connection():
    """
    Supply a fabric SSH connection
    """
    with open(os.path.join(PROJECT_DIR, "config", "config.json")) as f:
        config = json.load(f)

    connection = fabric.connection.Connection(
        f"{config['upload']['user']}@{config['upload']['host']}",
        connect_kwargs={"password": config["upload"]["password"]},
        connect_timeout=5,
    )

    # run the respective test
    yield connection

    connection.close()
