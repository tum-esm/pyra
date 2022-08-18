import json
import os
from packages.core.utils import Astronomy, with_filelock, types
from .config_validation import ConfigValidation

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
        an AssertionError if the file is not valid.
        """
        file_is_valid, validation_exception = ConfigValidation.check_current_config_file()
        assert file_is_valid, str(validation_exception)
        with open(CONFIG_FILE_PATH, "r") as f:
            _CONFIG = json.load(f)

        Astronomy.CONFIG = _CONFIG
        return _CONFIG
