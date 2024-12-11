import abc
import re
import threading

from packages.core import types, utils

logger = utils.Logger(origin="helios")


class AbstractThread(abc.ABC):
    """Abstract base class for all threads"""

    def __init__(self) -> None:
        """Initialize the thread instance. This does not start the
        thread but only initializes the instance that triggers the
        thread to start and stop correctly."""

        # credits to https://stackoverflow.com/a/1176023/8255842
        self.logger: utils.Logger = utils.Logger(
            origin=re.sub(r"(?<!^)(?=[A-Z])", "-", self.__class__.__name__).lower()
        )
        self.thread = self.get_new_thread_object()
        self.is_initialized = False

    def update_thread_state(self, config: types.Config) -> None:
        """Use `self.should_be_running` to determine if the thread
        should be running or not. If it should be running and it is
        not running, start the thread. If it should not be running
        and it is running, stop the thread."""

        should_be_running: bool = self.__class__.should_be_running(config)

        if should_be_running:
            if self.is_initialized:
                if self.thread.is_alive():
                    self.logger.debug("Thread is running correctly")
                else:
                    self.logger.debug("Thread has crashed, running teardown")
                    self.thread.join()
                    # set up a new thread instance for the next time the thread should start
                    self.thread = self.get_new_thread_object()
                    self.is_initialized = False
            else:
                self.logger.debug("Starting the thread")
                self.thread.start()
                self.is_initialized = True

        else:
            if self.is_initialized:
                self.logger.debug("Joining the thread")
                self.thread.join()
                self.thread = self.get_new_thread_object()
                self.is_initialized = False
            else:
                self.logger.debug("Thread is pausing")

    @staticmethod
    @abc.abstractmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

    @staticmethod
    @abc.abstractmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""

    @staticmethod
    @abc.abstractmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""
