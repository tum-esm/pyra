import json
import os
import shutil
from packages.core.utils import with_filelock, update_dict_recursively, PersistentStateTypes
from .plc_interface import EMPTY_PLC_STATE

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")

RUNTIME_DATA_PATH = os.path.join(PROJECT_DIR, "runtime-data")
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")

PERSISTENT_STATE_FILE_PATH = os.path.join(PROJECT_DIR, "logs", "persistent-state.json")


EMPTY_STATE_OBJECT: dict = {
    "helios_indicates_good_conditions": None,
    "measurements_should_be_running": False,
    "enclosure_plc_readings": EMPTY_PLC_STATE.to_dict(),
    "os_state": {
        "cpu_usage": None,
        "memory_usage": None,
        "last_boot_time": None,
        "filled_disk_space_fraction": None,
    },
}

EMPTY_PERSISTENT_STATE_OBJECT: PersistentStateTypes.PartialDict = {
    "active_opus_macro_id": None,
    "current_exceptions": [],
}

# TODO: Validate structure with cerberus (assertion)
#       we could possibly use pydantic for that


class StateInterface:
    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def initialize() -> None:
        """
        This will create two files:

        1. runtime-data/state.json: {
            "helios_indicates_good_conditions": ...,
            "measurements_should_be_running": ...,
            "enclosure_plc_readings": {...},
            "os_state": {...}
        }

        2. logs/persistent-state.json: {
            "active_opus_macro_id": ...,
            "current_exceptions": []
        }

        The state.json file will be cleared with every restart
        of PYRA Core. The persistent-state.json will only be
        created, when it does not exist yet.
        """

        # clear runtime-data directory
        if os.path.exists(RUNTIME_DATA_PATH):
            shutil.rmtree(RUNTIME_DATA_PATH)
        os.mkdir(RUNTIME_DATA_PATH)

        # create the state file
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(EMPTY_STATE_OBJECT, f, indent=4)

        # possibly create the persistent state file
        if not os.path.isfile(PERSISTENT_STATE_FILE_PATH):
            with open(PERSISTENT_STATE_FILE_PATH, "w") as f:
                json.dump(EMPTY_PERSISTENT_STATE_OBJECT, f, indent=4)

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def read() -> dict:
        """Read the state file and return its content"""
        with open(STATE_FILE_PATH, "r") as f:
            new_object = json.load(f)
            # TODO: PersistentStateTypes.validate_object(new_object)
            return new_object

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def read_persistent() -> PersistentStateTypes.Dict:
        """Read the persistent state file and return its content"""
        with open(PERSISTENT_STATE_FILE_PATH, "r") as f:
            new_object: PersistentStateTypes.Dict = json.load(f)
            PersistentStateTypes.validate_object(new_object)
            return new_object

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def update(update: dict) -> None:
        """
        Update the (persistent) state file and return its content.
        The update object should only include the properties to be
        changed in contrast to containing the whole file.
        """

        with open(STATE_FILE_PATH, "r") as f:
            current_state = json.load(f)

        new_state = update_dict_recursively(current_state, update)
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def update_persistent(update: PersistentStateTypes.PartialDict) -> None:
        """
        Update the (persistent) state file and return its content.
        The update object should only include the properties to be
        changed in contrast to containing the whole file.
        """

        with open(PERSISTENT_STATE_FILE_PATH, "r") as f:
            current_state = json.load(f)
            PersistentStateTypes.validate_object(current_state)

        new_state = update_dict_recursively(current_state, update)
        with open(PERSISTENT_STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)
