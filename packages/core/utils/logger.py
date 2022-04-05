import logging
import os
from filelock import FileLock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
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
logging.getLogger("filelock").setLevel(logging.WARNING)


class Logger:
    @staticmethod
    def debug(message: str, origin="pyra.core"):
        with FileLock(LOGS_LOCK_PATH):
            logging.getLogger(origin).debug(message)

    @staticmethod
    def info(message: str, origin="pyra.core"):
        with FileLock(LOGS_LOCK_PATH):
            logging.getLogger(origin).info(message)

    @staticmethod
    def warning(message: str, origin="pyra.core"):
        with FileLock(LOGS_LOCK_PATH):
            logging.getLogger(origin).warning(message)

    @staticmethod
    def critical(message: str, origin="pyra.core"):
        with FileLock(LOGS_LOCK_PATH):
            logging.getLogger(origin).critical(message)

    @staticmethod
    def error(message: str, origin="pyra.core"):
        with FileLock(LOGS_LOCK_PATH):
            logging.getLogger(origin).error(message)
