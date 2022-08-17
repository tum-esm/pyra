import abc
import threading
from typing import Optional
from packages.core.utils.functions.logger import Logger


class AbstractThreadBase(abc.ABC):
    """
    An abstract base class for thread classes used in PYRA
    """

    def __init__(self, config: dict, logger_origin: str):
        self.__thread: Optional[threading.Thread] = None
        self.__logger: Logger = Logger(origin=logger_origin)
        self.config: dict = config

    def update_thread_state(self, new_config: dict):
        """
        Make sure that the thread loop is (not) running,
        based on config.upload
        """
        self.config = new_config

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
    def should_be_running(self) -> bool:
        """Should the thread be running? (based on config.upload)"""
        pass

    @abc.abstractmethod
    def main(self):
        """Main entrypoint of the thread"""
        pass
