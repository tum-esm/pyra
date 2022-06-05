import logging
import os
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INFO_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "info.log")
DEBUG_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "debug.log")
LOG_FILES_LOCK = os.path.join(PROJECT_DIR, "logs", "logs.lock")

# TODO: Figure out why duplicate logs are written to the INFO log files

# Set up logging module
_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, filename=DEBUG_LOG_FILE, format=_format)
_info_log_handler = logging.FileHandler(filename=INFO_LOG_FILE, mode="a")
_info_log_handler.setLevel(logging.INFO)
_info_log_handler.setFormatter(logging.Formatter(_format))

# Hide irrelevant logs from libraries
logging.getLogger("filelock").setLevel(logging.WARNING)


def with_filelock(function):
    def locked_function(*args, **kwargs):
        with filelock.FileLock(LOG_FILES_LOCK):
            return function(*args, **kwargs)

    return locked_function


class Logger:
    def __init__(self, origin="pyra.core"):
        self.logger = logging.getLogger(origin)
        self.logger.addHandler(_info_log_handler)

    @with_filelock
    def debug(self, message: str):
        self.logger.debug(message)

    @with_filelock
    def info(self, message: str):
        self.logger.info(message)

    @with_filelock
    def warning(self, message: str):
        self.logger.warning(message)

    @with_filelock
    def critical(self, message: str):
        self.logger.critical(message)

    @with_filelock
    def error(self, message: str):
        self.logger.error(message)

    @with_filelock
    def exception(self, message: str):
        self.logger.exception(message)
