import json
import os
import shutil

from .plc_interface import EMPTY_PLC_STATE
from packages.core.utils import with_filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")

RUNTIME_DATA_PATH = os.path.join(PROJECT_DIR, "runtime-data")
STATE_FILE_PATH = os.path.join(RUNTIME_DATA_PATH, "state.json")
VBDSD_IMG_DIR = os.path.join(RUNTIME_DATA_PATH, "vbdsd")


# TODO: Rename as CoreStateInterface
# TODO: Make Interface responses statically typed


class StateInterface:
    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def initialize() -> None:
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
                    "automation_should_be_running": False,
                    "enclosure_plc_readings": EMPTY_PLC_STATE.to_dict(),
                },
                f,
                indent=4,
            )

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def read() -> dict:
        with open(STATE_FILE_PATH, "r") as f:
            return json.load(f)

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def update(update: dict):
        with open(STATE_FILE_PATH, "r") as f:
            _STATE = json.load(f)
        with open(STATE_FILE_PATH, "w") as f:
            json.dump({**_STATE, **update}, f, indent=4)
