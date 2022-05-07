import json
import os
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
STATE_FILE_PATH = f"{PROJECT_DIR}/config/state.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"


def with_filelock(function):
    def locked_function(*args, **kwargs):
        with filelock.FileLock(CONFIG_LOCK_PATH):
            return function(*args, **kwargs)

    return locked_function


class State:
    @staticmethod
    @with_filelock
    def initialize():
        os.remove(STATE_FILE_PATH)
        with open(STATE_FILE_PATH, "w") as f:
            json.dump({"vbdsd_evaluation_result": False, "continuous_readings": []}, f)

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
