import os
import threading
import psutil
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils

logger = utils.Logger(origin="camtracker")


class CamTrackerThread(AbstractThread):
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=CamTrackerThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        pass
