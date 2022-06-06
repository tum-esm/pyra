import json
import os
import shutil
import pytest

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_FILE_PATH_TMP = os.path.join(PROJECT_DIR, "config", "config.original.json")


@pytest.fixture()
def original_config():
    # save original config.json for later
    assert os.path.isfile(CONFIG_FILE_PATH), "config.json does not exist"
    assert not os.path.isfile(
        CONFIG_FILE_PATH_TMP
    ), "config.original.json already exist"

    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        raise Exception("config.json is invalid")

    shutil.copy(CONFIG_FILE_PATH, CONFIG_FILE_PATH_TMP)

    # run the respective test
    yield config

    # restore original config.json
    if os.path.isfile(CONFIG_FILE_PATH):
        os.remove(CONFIG_FILE_PATH)
    assert os.path.isfile(
        CONFIG_FILE_PATH_TMP
    ), "config.original.json does not exist anymore"
    os.rename(CONFIG_FILE_PATH_TMP, CONFIG_FILE_PATH)
