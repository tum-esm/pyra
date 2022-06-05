import json
import os
import shutil
import filelock
from packages.core.utils.astronomy import Astronomy
from packages.core.utils.validation import Validation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", "config.lock")

RUNTIME_DATA_PATH = os.path.join(PROJECT_DIR, "runtime-data")
STATE_FILE_PATH = os.path.join(RUNTIME_DATA_PATH, "state.json")
VBDSD_IMG_DIR = os.path.join(RUNTIME_DATA_PATH, "vbdsd")


# FileLock = Mark, that the config JSONs are being used and the
# CLI should not interfere. A file "config/config.lock" will be created
# and the existence of this file will make the next line wait.
def with_filelock(function):
    def locked_function(*args, **kwargs):
        with filelock.FileLock(CONFIG_LOCK_PATH):
            return function(*args, **kwargs)

    return locked_function


class StateInterface:
    @staticmethod
    @with_filelock
    def initialize():
        # clear runtime_data directory
        if os.path.exists(RUNTIME_DATA_PATH):
            shutil.rmtree(RUNTIME_DATA_PATH)
        os.mkdir(RUNTIME_DATA_PATH)
        os.mkdir(VBDSD_IMG_DIR)

        # write initial state.json file
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(
                {
                    "vbdsd_indicates_good_conditions": None,
                    "enclosure_plc_readings": [],
                    "automation_should_be_running": False,
                },
                f,
            )

    @staticmethod
    @with_filelock
    def read() -> dict:
        with open(STATE_FILE_PATH, "r") as f:
            return json.load(f)

    @staticmethod
    @with_filelock
    def update(update: dict):
        with open(STATE_FILE_PATH, "r") as f:
            _STATE = json.load(f)
        with open(STATE_FILE_PATH, "w") as f:
            json.dump({**_STATE, **update}, f)


class ConfigInterface:
    @staticmethod
    @with_filelock
    def read() -> dict:
        assert Validation.check_current_config()
        with open(CONFIG_FILE_PATH, "r") as f:
            _CONFIG = json.load(f)

        Astronomy.CONFIG = _CONFIG
        return _CONFIG
