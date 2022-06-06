import os
import shutil
import pytest

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_FILE_PATH_TMP = os.path.join(PROJECT_DIR, "config", "config.tmp.json")


@pytest.fixture()
def config_file():
    # save config.json in another file
    assert os.path.isfile(CONFIG_FILE_PATH)
    assert not os.path.isfile(CONFIG_FILE_PATH_TMP)
    shutil.copy(CONFIG_FILE_PATH, CONFIG_FILE_PATH_TMP)

    # run the respective test
    yield

    # restore old config.json
    if os.path.isfile(CONFIG_FILE_PATH):
        os.remove(CONFIG_FILE_PATH)
    assert os.path.isfile(CONFIG_FILE_PATH_TMP)
    os.rename(CONFIG_FILE_PATH_TMP, CONFIG_FILE_PATH)
