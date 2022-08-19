import json
import os
from typing import Any
from packages.core.utils import Astronomy, with_filelock, types

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")


class ConfigInterface:
    @staticmethod
    @with_filelock(CONFIG_LOCK_PATH)
    def read() -> types.ConfigDict:
        """
        Read the contents of the current config.json file.
        The function will validate its integrity and raises
        an Exception if the file is not valid.
        """
        with open(CONFIG_FILE_PATH, "r") as f:
            new_object: Any = json.load(f)
            types.validate_config_dict(new_object)
            config: types.ConfigDict = new_object

        Astronomy.CONFIG = config
        return config
