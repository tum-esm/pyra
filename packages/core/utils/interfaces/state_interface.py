import json
import os
import shutil

from packages.core.utils import update_dict_recursively

from .plc_interface import EMPTY_PLC_STATE
from packages.core.utils import with_filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")

RUNTIME_DATA_PATH = os.path.join(PROJECT_DIR, "runtime-data")
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")

PERSISTENT_STATE_FILE_PATH = os.path.join(PROJECT_DIR, "logs", "persistent-state.json")


# TODO: Rename as CoreStateInterface
# TODO: Documentation


class StateInterface:
    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def initialize() -> None:
        # possibly create runtime_data directory
        if not os.path.exists(RUNTIME_DATA_PATH):
            os.mkdir(RUNTIME_DATA_PATH)

        # write initial state.json file
        new_state = {
            "vbdsd_indicates_good_conditions": None,
            "measurements_should_be_running": False,
            "enclosure_plc_readings": EMPTY_PLC_STATE.to_dict(),
            "os_state": {
                "cpu_usage": None,
                "memory_usage": None,
                "last_boot_time": None,
                "filled_disk_space_fraction": None,
            },
        }
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)

        # persistent state will not be overwritten with a restart of pyra-core
        if not os.path.isfile(PERSISTENT_STATE_FILE_PATH):
            new_persistent_state = {"active_opus_macro_id": None, "current_exceptions": []}
            with open(PERSISTENT_STATE_FILE_PATH, "w") as f:
                json.dump(new_persistent_state, f, indent=4)

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def read(persistent: bool = False) -> dict:
        file_path = PERSISTENT_STATE_FILE_PATH if persistent else STATE_FILE_PATH
        with open(file_path, "r") as f:
            return json.load(f)

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def update(update: dict, persistent: bool = False):
        file_path = PERSISTENT_STATE_FILE_PATH if persistent else STATE_FILE_PATH

        with open(file_path, "r") as f:
            current_state = json.load(f)

        new_state = update_dict_recursively(current_state, update)
        with open(file_path, "w") as f:
            json.dump(new_state, f, indent=4)
