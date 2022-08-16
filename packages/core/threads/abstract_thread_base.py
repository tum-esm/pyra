import abc
import threading
from typing import Callable
from packages.core.utils.functions.logger import Logger


class AbstractThreadBase(abc.ABC):
    """
    An abstract base class for thread classes used in PYRA
    """

    def __init__(self, logger_origin: str):
        self.__thread = None
        self.__logger = Logger(origin=logger_origin)

    def update_thread_state(self, config: dict):
        """
        Make sure that the thread loop is (not) running,
        based on config.upload
        """
        self.config = config

        is_running = (self.__thread is not None) and self.__thread.is_alive()
        should_be_running = self.should_be_running()

        if should_be_running and (not is_running):
            self.__logger.info("Starting the thread")
            self.__thread = threading.Thread(target=self.main)
            self.__thread.start()

        if (self.__thread is not None) and (not is_running):
            self.__logger.info("Thread has stopped")
            self.__thread.join()
            self.__thread = None

    @abc.abstractmethod
    def should_be_running(self, config: dict) -> bool:
        """Should the thread be running? (based on config.upload)"""
        pass

    @abc.abstractmethod
    def main(self):
        """Main entrypoint of the thread"""
        pass
