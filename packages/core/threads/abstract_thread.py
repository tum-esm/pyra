import abc
import threading
import time
from typing import Optional

from packages.core import types, utils


class AbstractThread(abc.ABC):
    """Abstract base class for all threads"""

    logger_origin: Optional[str] = None

    def __init__(
        self,
        state_lock: threading.Lock,
        logs_lock: threading.Lock,
    ) -> None:
        """Initialize the thread instance. This does not start the
        thread but only initializes the instance that triggers the
        thread to start and stop correctly."""

        assert self.__class__.logger_origin is not None
        self.logger: utils.Logger = utils.Logger(
            origin=self.__class__.logger_origin,
            lock=logs_lock,
        )
        self.thread = self.get_new_thread_object(
            state_lock=state_lock,
            logs_lock=logs_lock,
        )
        self.thread_start_time: Optional[float] = None
        self.state_lock: threading.Lock = logs_lock
        self.logs_lock: threading.Lock = logs_lock

    def update_thread_state(
        self,
        config: types.Config,
    ) -> bool:
        """Use `self.should_be_running` to determine if the thread
        should be running or not. If it should be running and it is
        not running, start the thread. If it should not be running
        and it is running, stop the thread.

        Returns True if the thread is running/pausing correctly, False
        otherwise."""

        should_be_running: bool = self.__class__.should_be_running(
            config, self.state_lock, self.logger
        )

        if should_be_running:
            if self.thread_start_time is not None:
                if self.thread.is_alive():
                    self.logger.debug("Thread is running correctly")
                    return True
                else:
                    now = time.time()
                    if (self.thread_start_time - now) <= 43199:  # 43200 seconds = 12 hours
                        self.logger.debug("Thread has crashed/stopped, running teardown")
                    self.thread.join()
                    self.thread_start_time = None
                    # set up a new thread instance for the next time the thread should start
                    self.thread = self.get_new_thread_object(
                        state_lock=self.state_lock,
                        logs_lock=self.logs_lock,
                    )
            else:
                self.logger.debug("Starting the thread")
                self.thread.start()
                self.thread_start_time = time.time()

        else:
            if self.thread_start_time is not None:
                self.logger.debug("Joining the thread")
                self.thread.join()
                self.thread = self.get_new_thread_object(
                    logs_lock=self.logs_lock,
                )
                self.thread_start_time = None
            else:
                self.logger.debug("Thread is pausing")
                return True

        return False

    @staticmethod
    @abc.abstractmethod
    def should_be_running(
        config: types.Config,
        state_lock: threading.Lock,
        logger: utils.Logger,
    ) -> bool:
        """Based on the config, should the thread be running or not?"""

    @staticmethod
    @abc.abstractmethod
    def get_new_thread_object(
        state_lock: threading.Lock,
        logs_lock: threading.Lock,
    ) -> threading.Thread:
        """Return a new thread object that is to be started."""

    @staticmethod
    @abc.abstractmethod
    def main(
        state_lock: threading.Lock,
        logs_lock: threading.Lock,
        headless: bool = False,
    ) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""
