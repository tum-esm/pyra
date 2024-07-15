from .abstract_thread import AbstractThread
from packages.core import types, utils, interfaces
import threading
import time


class ThingsBoardThread(AbstractThread):

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        # only upload when upload is configured
        if config.thingsboard is None:
            return False

        # don't upload in test mode
        if config.general.test_mode:
            return False

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=ThingsBoardThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="upload", just_print=headless)
        config = types.Config.load()
        assert config.thingsboard is not None

        while True:
            print(1)
            time.sleep(60)
