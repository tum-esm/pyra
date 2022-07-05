import json
import os
import filelock

from .config_validation import ConfigValidation
from packages.core.utils import Astronomy

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")

# TODO: Move this to a "decorators" directory
# FileLock = Mark, that the config JSONs are being used and the
# CLI should not interfere. A file "config/config.lock" will be created
# and the existence of this file will make the next line wait.
def with_filelock(file_lock_path):
    def wrapper(function):
        def locked_function(*args, **kwargs):
            with filelock.FileLock(file_lock_path):
                return function(*args, **kwargs)

        return locked_function

    return wrapper


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
