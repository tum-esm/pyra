from datetime import datetime
import os
import queue
import threading
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


class CameraError(Exception):
    pass


class _VBDSD:
    cam = None
    current_exposure = -12
    last_autoexposure_time = 0

    @staticmethod
    def init(camera_id: int, retries: int = 5):

        # TODO: Why is this necessary?
        # _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        # _VBDSD.cam.release()

        for _ in range(retries):
            _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            if _VBDSD.cam.isOpened():
                _VBDSD.update_camera_settings(
                    width=1280,
                    height=720,
                    exposure=-12,
                    brightness=64,
                    contrast=64,
                    saturation=0,
                    gain=0,
                )
                return
            else:
                time.sleep(2)

        raise Exception("could not initialize camera")

    @staticmethod
    def deinit():
        _VBDSD.cam.release()

    @staticmethod
    def update_camera_settings(
        exposure: int = None,
        brightness: int = None,
        contrast: int = None,
        saturation: int = None,
        gain: int = None,
        width: int = None,
        height: int = None,
    ):
        # which settings are available depends on the camera model.
        # however, this function will throw an AssertionError, when
        # the value could not be changed
        properties = {
            "width": (cv.CAP_PROP_FRAME_WIDTH, width),
            "height": (cv.CAP_PROP_FRAME_HEIGHT, height),
            "exposure": (cv.CAP_PROP_EXPOSURE, exposure),
            "brightness": (cv.CAP_PROP_EXPOSURE, brightness),
            "contrast": (cv.CAP_PROP_EXPOSURE, contrast),
            "saturation": (cv.CAP_PROP_EXPOSURE, saturation),
            "gain": (cv.CAP_PROP_EXPOSURE, gain),
        }
        for property_name in properties:
            key, value = properties[property_name]
            if value is not None:
                _VBDSD.cam.set(key, value)
                new_value = _VBDSD.cam.get(key)
                assert new_value == value, f"could not set {property_name} to {value}"

        # throw away some images after changing settings. I don't know
        # why this is necessary, but it resolved a lot of issues
        for _ in range(2):
            _VBDSD.cam.read()

    @staticmethod
    def take_image(retries: int = 5) -> cv.Mat:
        assert _VBDSD.cam is not None, "camera is not initialized yet"
        if not _VBDSD.cam.isOpened():
            raise CameraError("camera is not open")
        for _ in range(retries + 1):
            ret, frame = _VBDSD.cam.read()
            if ret:
                return frame
        raise CameraError("could not take image")

    @staticmethod
    def adjust_exposure():
        """
        set exposure to the value where the overall
        mean pixel value color is closest to 100
        """
        exposure_results = []
        for e in range(-12, 0):
            _VBDSD.update_camera_settings(exposure=e)
            image = _VBDSD.take_image()
            exposure_results.append({"exposure": e, "mean": np.mean(image)})
        new_exposure = min(exposure_results, key=lambda r: abs(r["mean"] - 100))["exposure"]
        logger.debug(f"exposure results: {exposure_results}")

        if new_exposure != _VBDSD.current_exposure:
            _VBDSD.update_camera_settings(exposure=new_exposure)
            logger.info(f"changing exposure: {_VBDSD.current_exposure} -> {new_exposure}")

    @staticmethod
    def determine_frame_status(frame: cv.Mat, save_image: bool) -> int:
        # transform image from 1280x720 to 640x360
        downscaled_image = cv.resize(frame, (640, 360))

        # for each rgb pixel [234,234,234] only consider the gray value (234)
        single_valued_pixels = downscaled_image.mean(axis=2, dtype=np.float32)

        # apply kmeans (bin colors to the 3 most dominant ones)
        _, raw_labels, raw_centers = cv.kmeans(
            data=single_valued_pixels.flatten(),
            K=3,
            bestLabels=None,
            criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0),
            attempts=5,
            flags=cv.KMEANS_RANDOM_CENTERS,
        )

        # determine the three color values
        centers: list[int] = list(raw_centers.flatten())
        _, middle_color, bright_color = list(sorted(centers))

        # count the occurances of each color
        h = np.histogram(raw_labels, bins=[0, 1, 2, 3])[0]
        hs: dict[int, int] = {centers[i]: h[i] for i in range(3)}
        bright_color_count = hs[bright_color]
        middle_color_count = hs[middle_color]

        # TODO: the values below should be adjusted by looking at the ifgs directly
        status = 1

        # the shadows have to make up 7.5% - 40% of the circle
        shadow_fraction = middle_color_count / (middle_color_count + bright_color_count)
        if shadow_fraction < 0.075 or shadow_fraction > 0.40:
            status = 0

        # the shadow color should be at least 40 (of 255) points darker
        shadow_offset = bright_color - middle_color
        if shadow_offset < 30:
            status = 0

        if save_image:
            image_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            raw_image_path = os.path.join(IMG_DIR, f"{image_timestamp}-{status}-raw.jpg")
            cv.imwrite(raw_image_path, frame)

            processed_image_path = os.path.join(
                IMG_DIR, f"{image_timestamp}-{status}-processed.jpg"
            )
            color_centers = [[np.mean(c)] * 3 for c in list(raw_centers)]
            flat_processed_frame = np.uint8(color_centers)[raw_labels.flatten()]
            processed_frame = flat_processed_frame.reshape((downscaled_image.shape))
            cv.imwrite(processed_image_path, processed_frame)

        return status

    @staticmethod
    def run(save_image: bool) -> int:
        # run autoexposure function every 3 minutes
        if (time.time() - _VBDSD.last_autoexposure_time) > 180:
            _VBDSD.adjust_exposure()

        try:
            frame = _VBDSD.take_image()
            return _VBDSD.determine_frame_status(frame, save_image)
        except CameraError:
            return -1


class VBDSD_Thread:
    def __init__(self):
        self.__thread = None
        self.__shared_queue = queue.Queue()

    def start(self):
        """
        Start a thread using the multiprocessing library
        """
        logger.info("Starting thread")
        self.__thread = threading.Thread(target=VBDSD_Thread.main, args=(self.__shared_queue,))
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
                    _VBDSD.deinit()
                    break
            except queue.Empty:
                pass

            try:
                start_time = time.time()
                _CONFIG = ConfigInterface.read()

                # init camera connection
                if _VBDSD.cam is None:
                    logger.info(f"Initializing VBDSD camera")
                    _VBDSD.init_cam(_CONFIG["vbdsd"]["camera_id"])

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

                # take a picture and process it: status is in [-1,0,1]
                status = _VBDSD.run(_CONFIG["vbdsd"]["save_images"])
                if status == -1:
                    logger.debug(f"Could not take image")

                # append sun status to status history
                status_history.append(0 if (status == -1) else status)
                logger.debug(
                    f"New VBDSD status: {status}. Current history: {status_history.get()}"
                )

                # evaluate sun state only if list is filled
                new_state = None
                if status_history.size() == status_history.maxsize():
                    score = status_history.sum() / status_history.size()
                    new_state = score > _CONFIG["vbdsd"]["measurement_threshold"]

                if current_state != new_state:
                    logger.info(
                        f"State change: {'BAD -> GOOD' if (new_state == True) else 'GOOD -> BAD'}"
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

            except Exception as e:
                status_history.empty()
                _VBDSD.deinit()

                logger.error("Error within VBDSD thread: trying again in 60 seconds")
                logger.exception(e)

                time.sleep(60)
