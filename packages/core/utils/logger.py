import logging
import os
from filelock import FileLock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
LOGS_LOCK_PATH = f"{PROJECT_DIR}/logs/logs.lock"

# Setup logging module
logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.DEBUG, filename=f"{PROJECT_DIR}/logs/debug.log", format=logging_format
)
logging_info_handler = logging.FileHandler(
    filename=f"{PROJECT_DIR}/logs/info.log", mode="a"
)
logging_info_handler.setLevel(logging.INFO)
logging_info_handler.setFormatter(logging.Formatter(logging_format))
logger = logging.getLogger("pyra.core")
logger.addHandler(logging_info_handler)

# Hide irrelevant logs from module "filelock"
logging.getLogger("filelock").setLevel(logging.WARNING)


class Logger:
    def __init__(self, origin="pyra.core"):
        self.logger = logging.getLogger(origin)

    def debug(self, message: str):
        with FileLock(LOGS_LOCK_PATH):
            self.logger.debug(message)

    def info(self, message: str):
        with FileLock(LOGS_LOCK_PATH):
            self.logger.info(message)

    def warning(self, message: str):
        with FileLock(LOGS_LOCK_PATH):
            self.logger.warning(message)

    def critical(self, message: str):
        with FileLock(LOGS_LOCK_PATH):
            self.logger.critical(message)

    def error(self, message: str):
        with FileLock(LOGS_LOCK_PATH):
            self.logger.error(message)

    def exception(self, message: str):
        with FileLock(LOGS_LOCK_PATH):
            self.logger.exception(message)
