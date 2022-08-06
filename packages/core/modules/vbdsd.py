from datetime import datetime
import os
import queue
from threading import Thread
import time
import cv2 as cv
import numpy as np
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
    RingList,
    Astronomy,
)

logger = Logger(origin="vbdsd")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
IMG_DIR = os.path.join(PROJECT_DIR, "logs", "vbdsd")
_CONFIG = None


class _VBDSD:
    cam = None

    @staticmethod
    def init_cam(retries: int = 5):
        camera_id = 0

        _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        _VBDSD.cam.release()

        for _ in range(retries):
            _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            if _VBDSD.cam.isOpened():
                _VBDSD.cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)  # width
                _VBDSD.cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)  # height
                _VBDSD.update_camera_settings(
                    exposure=-12, brightness=64, contrast=64, saturation=0, gain=0
                )
                print(f"using backend {_VBDSD.cam.getBackendName()}")
                return
            else:
                time.sleep(2)

        raise Exception("could not initialize camera")

    @staticmethod
    def update_camera_settings(
        exposure: int = None,
        brightness: int = None,
        contrast: int = None,
        saturation: int = None,
        gain: int = None,
    ):
        if exposure is not None:
            _VBDSD.cam.set(cv.CAP_PROP_EXPOSURE, exposure)
            assert (
                _VBDSD.cam.get(cv.CAP_PROP_EXPOSURE) == exposure
            ), f"could not set exposure to {exposure}"
        if brightness is not None:
            _VBDSD.cam.set(cv.CAP_PROP_BRIGHTNESS, brightness)
            assert (
                _VBDSD.cam.get(cv.CAP_PROP_BRIGHTNESS) == brightness
            ), f"could not set brightness to {brightness}"
        if contrast is not None:
            _VBDSD.cam.set(cv.CAP_PROP_CONTRAST, contrast)
            assert (
                _VBDSD.cam.get(cv.CAP_PROP_CONTRAST) == contrast
            ), f"could not set contrast to {contrast}"
        if saturation is not None:
            _VBDSD.cam.set(cv.CAP_PROP_SATURATION, saturation)
            assert (
                _VBDSD.cam.get(cv.CAP_PROP_SATURATION) == saturation
            ), f"could not set saturation to {saturation}"
        if gain is not None:
            _VBDSD.cam.set(cv.CAP_PROP_GAIN, gain)
            assert _VBDSD.cam.get(cv.CAP_PROP_GAIN) == gain, f"could not set gain to {gain}"

        # throw away some images after changing settings
        for _ in range(2):
            _VBDSD.cam.read()

    @staticmethod
    def take_image(retries: int = 5):
        assert _VBDSD.cam is not None, "camera is not initialized yet"
        assert _VBDSD.cam.isOpened(), "camera is not open"
        for _ in range(retries + 1):
            ret, frame = _VBDSD.cam.read()
            if ret:
                return frame
        raise Exception("could not take image")

    @staticmethod
    def get_best_exposure() -> int:
        """
        determine the exposure, where the overall
        mean pixel value color is closest to 100
        """
        exposure_results = []
        for e in range(-12, 0):
            _VBDSD.update_camera_settings(exposure=e)
            image = _VBDSD.take_image()
            exposure_results.append({"exposure": e, "mean": np.mean(image)})
        print(exposure_results)
        return min(exposure_results, key=lambda r: abs(r["mean"] - 100))["exposure"]


class VBDSD_Thread:
    def __init__(self):
        self.__thread = None
        self.__shared_queue = queue.Queue()

    def start(self):
        """
        Start a thread using the multiprocessing library
        """
        logger.info("Starting thread")
        self.__thread = Thread(target=VBDSD_Thread.main, args=(self.__shared_queue,))
        self.__thread.start()

    def is_running(self):
        return self.__thread is not None

    def stop(self):
        """
        Stop the thread and set the state to 'null'
        """

        logger.info("Sending termination signal")
        self.__shared_queue.put("stop")

        logger.info("Waiting for thread to terminate")
        self.__thread.join()

        logger.debug('Setting state to "null"')
        StateInterface.update({"vbdsd_indicates_good_conditions": None})

        self.__thread = None

    @staticmethod
    def main(shared_queue: queue.Queue, infinite_loop=True):
        global _CONFIG
        _CONFIG = ConfigInterface.read()

        status_history = RingList(_CONFIG["vbdsd"]["evaluation_size"])
        current_state = None

        while True:

            # Check for termination
            try:
                if shared_queue.get(block=False) == "stop":
                    break
            except queue.Empty:
                pass

            start_time = time.time()
            _CONFIG = ConfigInterface.read()

            # init camera connection
            if _VBDSD.cam is None:
                logger.info(f"Initializing VBDSD camera")
                _VBDSD.init_cam()

                # if connecting was not successful
                if _VBDSD.cam is None:
                    status_history.empty()
                    time.sleep(60)
                    continue

            # reinit if parameter changes
            new_size = _CONFIG["vbdsd"]["evaluation_size"]
            if status_history.maxsize() != new_size:
                logger.debug(
                    "Size of VBDSD history has changed: "
                    + f"{status_history.maxsize()} -> {new_size}"
                )
                status_history.reinitialize(new_size)

            # sleep while sun angle is too low
            if Astronomy.get_current_sun_elevation().is_within_bounds(
                None, _CONFIG["vbdsd"]["min_sun_elevation"] * Astronomy.units.deg
            ):
                logger.debug("Current sun elevation below minimum: Waiting 5 minutes")
                if current_state != None:
                    StateInterface.update({"vbdsd_indicates_good_conditions": False})
                    current_state = None
                    # reinit for next day
                    _VBDSD.reinit_settings()
                time.sleep(300)
                continue

            # take a picture and process it
            status, frame = _VBDSD.run(_CONFIG["vbdsd"]["save_images"])

            # retry with change_exposure(1) if status fail
            if status == -1:
                _VBDSD.change_exposure(1)
                status, frame = _VBDSD.run(_CONFIG["vbdsd"]["save_images"])

            # append sun status to status history
            status_history.append(max(status, 0))
            logger.debug(
                f"New VBDSD status: {status}. Current history: {status_history.get()}"
            )

            if frame is None:
                logger.debug(f"Could not take image")

            # evaluate sun state only if list is filled
            if status_history.size() == status_history.maxsize():
                score = status_history.sum() / status_history.size()
                new_state = score > _CONFIG["vbdsd"]["measurement_threshold"]
            else:
                new_state = None

            if current_state != new_state:
                logger.info(
                    f"State change: {'GOOD -> BAD' if current_state else 'BAD -> GOOD'}"
                )
                StateInterface.update({"vbdsd_indicates_good_conditions": new_state})
                current_state = new_state

            # wait rest of loop time
            elapsed_time = time.time() - start_time
            time_to_wait = _CONFIG["vbdsd"]["seconds_per_interval"] - elapsed_time
            if time_to_wait > 0:
                logger.debug(
                    f"Finished iteration, waiting {round(time_to_wait, 2)} second(s)."
                )
                time.sleep(time_to_wait)

            if not infinite_loop:
                return status_history
