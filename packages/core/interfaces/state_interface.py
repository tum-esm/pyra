import json
import os
import shutil
from packages.core import types, utils

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")

RUNTIME_DATA_PATH = os.path.join(PROJECT_DIR, "runtime-data")
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")

PERSISTENT_STATE_FILE_PATH = os.path.join(PROJECT_DIR, "logs", "persistent-state.json")


EMPTY_STATE_OBJECT: types.StateDict = {
    "helios_indicates_good_conditions": None,
    "measurements_should_be_running": False,
    "enclosure_plc_readings": {
        "last_read_time": None,
        "actors": {
            "fan_speed": None,
            "current_angle": None,
        },
        "control": {
            "auto_temp_mode": None,
            "manual_control": None,
            "manual_temp_mode": None,
            "sync_to_tracker": None,
        },
        "sensors": {
            "humidity": None,
            "temperature": None,
        },
        "state": {
            "cover_closed": None,
            "motor_failed": None,
            "rain": None,
            "reset_needed": None,
            "ups_alert": None,
        },
        "power": {
            "camera": None,
            "computer": None,
            "heater": None,
            "router": None,
            "spectrometer": None,
        },
        "connections": {
            "camera": None,
            "computer": None,
            "heater": None,
            "router": None,
            "spectrometer": None,
        },
    },
    "os_state": {
        "cpu_usage": None,
        "memory_usage": None,
        "last_boot_time": None,
        "filled_disk_space_fraction": None,
    },
}

EMPTY_PERSISTENT_STATE_OBJECT: types.PersistentStateDict = {
    "active_opus_macro_id": None,
    "current_exceptions": [],
}

logger = utils.Logger(origin="state-interface")


class StateInterface:
    @staticmethod
    @utils.with_filelock(STATE_LOCK_PATH, timeout=10)
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
    @utils.with_filelock(STATE_LOCK_PATH, timeout=10)
    def read() -> types.StateDict:
        """Read the state file and return its content"""
        try:
            with open(STATE_FILE_PATH, "r") as f:
                new_object: types.StateDict = json.load(f)
                types.validate_state_dict(new_object)
                return new_object
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("reinitializing the corrupted state file")
            with open(STATE_FILE_PATH, "w") as f:
                json.dump(EMPTY_STATE_OBJECT, f, indent=4)

    @staticmethod
    @utils.with_filelock(STATE_LOCK_PATH, timeout=10)
    def read_persistent() -> types.PersistentStateDict:
        """Read the persistent state file and return its content"""
        try:
            with open(PERSISTENT_STATE_FILE_PATH, "r") as f:
                new_object: types.PersistentStateDict = json.load(f)
                types.validate_persistent_state_dict(new_object)
                return new_object
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("reinitializing the corrupted persistent state file")
            with open(PERSISTENT_STATE_FILE_PATH, "w") as f:
                json.dump(EMPTY_PERSISTENT_STATE_OBJECT, f, indent=4)

    @staticmethod
    @utils.with_filelock(STATE_LOCK_PATH, timeout=10)
    def update(update: types.StateDictPartial) -> None:
        """
        Update the (persistent) state file and return its content.
        The update object should only include the properties to be
        changed in contrast to containing the whole file.
        """
        current_state = StateInterface.read()
        new_state = utils.update_dict_recursively(current_state, update)
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)

    @staticmethod
    @utils.with_filelock(STATE_LOCK_PATH, timeout=10)
    def update_persistent(update: types.PersistentStateDictPartial) -> None:
        """
        Update the (persistent) state file and return its content.
        The update object should only include the properties to be
        changed in contrast to containing the whole file.
        """

        current_state = StateInterface.read_persistent()
        new_state = utils.update_dict_recursively(current_state, update)
        with open(PERSISTENT_STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)
