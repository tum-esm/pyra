import logging
import os
import filelock

dir = os.path.dirname
LOGS_DIR = dir(dir(dir(dir(os.path.abspath(__file__))))) + "/logs"

# Set up logging module
_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, filename=LOGS_DIR + "/debug.log", format=_fmt)
_info_log_handler = logging.FileHandler(filename=LOGS_DIR + "/info.log", mode="a")
_info_log_handler.setLevel(logging.INFO)
_info_log_handler.setFormatter(logging.Formatter(_fmt))

# Hide irrelevant logs from libraries
logging.getLogger("filelock").setLevel(logging.WARNING)


def with_filelock(function):
    def locked_function(*args, **kwargs):
        with filelock.FileLock(LOGS_DIR + "/logs.lock"):
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
