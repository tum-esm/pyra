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


def update_dict_rec(old_object, new_object):
    if old_object is None or new_object is None:
        return new_object

    if type(old_object) == dict:
        assert type(new_object) == dict
        updated_dict = {}
        for key in old_object.keys():
            if key in new_object:
                updated_dict[key] = update_dict_rec(old_object[key], new_object[key])
            else:
                updated_dict[key] = old_object[key]
        return updated_dict
    else:
        if type(old_object) in [int, float]:
            assert type(new_object) in [int, float]
        else:
            assert type(old_object) == type(new_object)
        return new_object


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

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def read() -> dict:
        with open(STATE_FILE_PATH, "r") as f:
            return json.load(f)

    @staticmethod
    @with_filelock(STATE_LOCK_PATH)
    def update(update: dict):
        with open(STATE_FILE_PATH, "r") as f:
            current_state = json.load(f)

        new_state = update_dict_rec(current_state, update)
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(new_state, f, indent=4)
