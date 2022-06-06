import json
import os
import shutil
import pytest

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))

CONFIG_FILE_PATHS = {
    "actual": os.path.join(PROJECT_DIR, "config", "config.json"),
    "temporary": os.path.join(PROJECT_DIR, "config", "config.original.json"),
}
INFO_LOG_PATHS = {
    "actual": os.path.join(PROJECT_DIR, "logs", "info.log"),
    "temporary": os.path.join(PROJECT_DIR, "logs", "info.original.log"),
}
DEBUG_LOGS_PATHS = {
    "actual": os.path.join(PROJECT_DIR, "logs", "debug.log"),
    "temporary": os.path.join(PROJECT_DIR, "logs", "debug.original.log"),
}
LOG_PATHSS = [INFO_LOG_PATHS, DEBUG_LOGS_PATHS]


def save_file(paths: dict):
    if os.path.isfile(paths["temporary"]):
        os.remove(paths["temporary"])
    shutil.copy(paths["actual"], paths["temporary"])


def restore_file(paths: dict):
    if os.path.isfile(paths["actual"]):
        os.remove(paths["actual"])
    assert os.path.isfile(
        paths["temporary"]
    ), f'{paths["temporary"]} does not exist anymore'
    os.rename(paths["temporary"], paths["actual"])


@pytest.fixture()
def original_config():
    # save original config.json for later
    assert os.path.isfile(CONFIG_FILE_PATHS["actual"]), "config.json does not exist"
    try:
        with open(CONFIG_FILE_PATHS["actual"], "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        raise Exception("config.json is invalid")

    # save original config.json for later
    save_file(CONFIG_FILE_PATHS)

    # run the respective test
    yield config

    # restore original config.json
    restore_file(CONFIG_FILE_PATHS)


@pytest.fixture()
def original_log_files():
    # save original logs for later
    for log_paths in LOG_PATHSS:
        if not os.path.isfile(log_paths["actual"]):
            with open(log_paths["actual"], "w") as f:
                pass
        save_file(log_paths)

    # run the respective test
    yield

    # restore original config.json
    for log_paths in LOG_PATHSS:
        restore_file(log_paths)
