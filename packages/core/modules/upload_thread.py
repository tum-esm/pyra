from datetime import datetime
import os
import queue
import threading
import time
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
)

logger = Logger(origin="upload")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


def is_valid_date(date_string: str):
    try:
        day_ending = datetime.strptime(f"{date_string} 23:59:59", "%Y%m%d %H:%M:%S")
        seconds_since_day_ending = (datetime.now() - day_ending).total_seconds()
        assert seconds_since_day_ending >= 3600
        return True
    except (ValueError, AssertionError):
        return False


def get_directories_to_be_uploaded(ifg_src_path) -> list[str]:
    if not os.path.isdir(ifg_src_path):
        return []

    return list(
        filter(
            lambda f: os.path.isdir(os.path.join(ifg_src_path, f)) and is_valid_date(f),
            os.listdir(ifg_src_path),
        )
    )


class UploadThread:
    def __init__(self):
        self.__thread = None
        self.__shared_queue = None

    def start(self):
        """
        Start the thread using the threading library
        """
        logger.info("Starting thread")
        self.__shared_queue = queue.Queue()
        self.__thread = threading.Thread(target=UploadThread.main, args=(self.__shared_queue,))
        self.__thread.start()

    def is_running(self):
        return self.__thread is not None

    def stop(self):
        """
        Send a stop-signal to the thread and wait for its termination
        """

        assert self.__shared_queue is not None

        logger.info("Sending termination signal")
        self.__shared_queue.put("stop")

        logger.info("Waiting for thread to terminate")
        self.__thread.join()
        self.__thread = None
        self.__shared_queue = None

        logger.info("Stopped the thread")

    @staticmethod
    def main(shared_queue: queue.Queue):
        while True:
            config = ConfigInterface.read()

            # Check for termination
            try:
                if (
                    (config["upload"] is None)
                    or (not config["upload"]["is_active"])
                    or (shared_queue.get(block=False) == "stop")
                ):
                    break
            except queue.Empty:
                pass

            start_time = time.time()

            for d in get_directories_to_be_uploaded(config["upload"]["src_directory"]):
                pass

            # TODO: 4. loop over each directory and use the DirectoryUploadClient
            # TODO: 5. Figure out where ifgs lie on system
            # TODO: 6. Implement datalogger upload

            elapsed_time = time.time() - start_time
            time_to_wait = 5 - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
