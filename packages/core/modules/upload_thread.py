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


def get_directories_to_be_uploaded(ifg_src_dir):
    pass


class UploadThread:
    def __init__(self):
        self.__thread = None
        self.__shared_queue = queue.Queue()

    def start(self):
        """
        Start the thread using the threading library
        """
        logger.info("Starting thread")
        self.__thread = threading.Thread(target=UploadThread.main, args=(self.__shared_queue,))
        self.__thread.start()

    def is_running(self):
        return self.__thread is not None

    def stop(self):
        """
        Send a stop-signal to the thread and wait for its termination
        """

        logger.info("Sending termination signal")
        self.__shared_queue.put("stop")

        logger.info("Waiting for thread to terminate")
        self.__thread.join()
        self.__thread = None

        logger.info("Stopped the thread")

    @staticmethod
    def main(shared_queue: queue.Queue):
        while True:
            # Check for termination
            try:
                if shared_queue.get(block=False) == "stop":
                    break
            except queue.Empty:
                pass

            start_time = time.time()

            # TODO: 1. add upload stuff to config
            # TODO: 2. determine directories to be uploaded
            # TODO: 3. loop over each directory and use the DirectoryUploadClient
            # TODO: 4. make the client use threads -> still process one directory at a time but upload individual files in parallel
            # TODO: 5. Figure out where ifgs lie on system
            # TODO: 6. Implement datalogger upload

            elapsed_time = time.time() - start_time
            time_to_wait = 5 - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
