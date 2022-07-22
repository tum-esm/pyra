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
STATE_FILE_PATH = os.path.join(RUNTIME_DATA_PATH, "runtime-data", "state.json")
VBDSD_IMG_DIR = os.path.join(PROJECT_DIR, "runtime-data", "vbdsd")

PERSISTENT_STATE_FILE_PATH = os.path.join(PROJECT_DIR, "logs", "persistent-state.json")


# TODO: Rename as CoreStateInterface
# TODO: Documentation


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
        new_state = {
            "vbdsd_indicates_good_conditions": None,
            "measurements_should_be_running": False,
            "enclosure_plc_readings": EMPTY_PLC_STATE.to_dict(),
            "os_state": {
                "average_system_load": {
                    "last_1_minute": None,
                    "last_5_minutes": None,
                    "last_15_minutes": None,
                },
                "cpu_usage": None,
                "memory_usage": None,
                "last_boot_time": None,
                "filled_disk_space_fraction": None,
            },
        }
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)

        # persistent state will not be removed with a restart of pyra-core
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
