import json
import os
from packages.core.utils import Astronomy, with_filelock

from .config_validation import ConfigValidation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")


# TODO: Make config interface statically typed


class ConfigInterface:
    @staticmethod
    @with_filelock(CONFIG_LOCK_PATH)
    def read() -> dict:
        assert ConfigValidation.check_current_config_file()
        with open(CONFIG_FILE_PATH, "r") as f:
            _CONFIG = json.load(f)

        Astronomy.CONFIG = _CONFIG
        return _CONFIG
