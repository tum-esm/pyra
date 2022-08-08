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
    ImageProcessing,
)

logger = Logger(origin="vbdsd")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
IMG_DIR = os.path.join(PROJECT_DIR, "logs", "vbdsd")
AUTOEXPOSURE_IMG_DIR = os.path.join(PROJECT_DIR, "logs", "vbdsd-autoexposure")
_CONFIG = None


class CameraError(Exception):
    pass


class _VBDSD:
    cam = None
    current_exposure = None
    last_autoexposure_time = 0
    available_exposures = None

    @staticmethod
    def init(camera_id: int, retries: int = 5):
        # TODO: Why is this necessary?
        _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        _VBDSD.cam.release()

        for _ in range(retries):
            _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            if _VBDSD.cam.isOpened():

                if _VBDSD.available_exposures is None:
                    _VBDSD.available_exposures = _VBDSD.get_available_exposures()
                    logger.debug(
                        f"determined available exposures: {_VBDSD.available_exposures}"
                    )
                    assert (
                        len(_VBDSD.available_exposures) > 0
                    ), "did not find any available exposures"

                _VBDSD.current_exposure = min(_VBDSD.available_exposures)
                _VBDSD.update_camera_settings(
                    width=1280,
                    height=720,
                    exposure=min(_VBDSD.available_exposures),
                    brightness=64,
                    contrast=64,
                    saturation=0,
                    gain=0,
                )
                return
            else:
                time.sleep(2)

        raise CameraError("could not initialize camera")

    @staticmethod
    def deinit():
        if _VBDSD.cam is not None:
            _VBDSD.cam.release()
            _VBDSD.cam = None

    @staticmethod
    def get_available_exposures() -> list[int]:
        possible_values = []
        for exposure in range(-20, 20):
            _VBDSD.cam.set(cv.CAP_PROP_EXPOSURE, exposure)
            if _VBDSD.cam.get(cv.CAP_PROP_EXPOSURE) == exposure:
                possible_values.append(exposure)

        return possible_values

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
            "brightness": (cv.CAP_PROP_BRIGHTNESS, brightness),
            "contrast": (cv.CAP_PROP_CONTRAST, contrast),
            "saturation": (cv.CAP_PROP_SATURATION, saturation),
            "gain": (cv.CAP_PROP_GAIN, gain),
        }
        for property_name in properties:
            key, value = properties[property_name]
            if value is not None:
                _VBDSD.cam.set(key, value)
                if property_name not in ["width", "height"]:
                    new_value = _VBDSD.cam.get(key)
                    assert (
                        new_value == value
                    ), f"could not set {property_name} to {value}, value is still at {new_value}"

        # throw away some images after changing settings. I don't know
        # why this is necessary, but it resolved a lot of issues
        for _ in range(2):
            _VBDSD.cam.read()

    @staticmethod
    def take_image(retries: int = 10, trow_away_white_images: bool = True) -> cv.Mat:
        assert _VBDSD.cam is not None, "camera is not initialized yet"
        if not _VBDSD.cam.isOpened():
            raise CameraError("camera is not open")
        for _ in range(retries + 1):
            ret, frame = _VBDSD.cam.read()
            if ret:
                if trow_away_white_images and np.mean(frame) > 240:
                    # image is mostly white
                    continue
                return frame
        raise CameraError("could not take image")

    @staticmethod
    def adjust_exposure():
        """
        set exposure to the value where the overall
        mean pixel value color is closest to 100
        """
        exposure_results = [{"exposure": e, "values": []} for e in _VBDSD.available_exposures]
        for i in range(3):
            for j, e in enumerate(_VBDSD.available_exposures):
                _VBDSD.update_camera_settings(exposure=e)
                img = _VBDSD.take_image(trow_away_white_images=False)
                mean_color = np.mean(img)
                exposure_results[j]["values"].append(mean_color)
                img = ImageProcessing.add_text_to_image(img, f"mean={round(mean_color, 3)}")
                cv.imwrite(
                    os.path.join(AUTOEXPOSURE_IMG_DIR, f"exposure-{e}-take-{j}.jpg"), img
                )

        logger.debug(f"exposure results: {exposure_results}")
        new_exposure = min(exposure_results, key=lambda r: abs(np.mean(r["values"]) - 50))[
            "exposure"
        ]

        if new_exposure != _VBDSD.current_exposure:
            _VBDSD.update_camera_settings(exposure=new_exposure)
            logger.info(f"changing exposure: {_VBDSD.current_exposure} -> {new_exposure}")
            _VBDSD.current_exposure = new_exposure

    @staticmethod
    def determine_frame_status(frame: cv.Mat, save_image: bool) -> int:
        # transform image from 1280x720 to 640x360
        downscaled_image = cv.resize(frame, None, fx=0.5, fy=0.5)

        # for each rgb pixel [234,234,234] only consider the gray value (234)
        single_valued_pixels = cv.cvtColor(downscaled_image, cv.COLOR_BGR2GRAY)

        # determine lense position and size from binary mask
        binary_mask = ImageProcessing.get_binary_mask(single_valued_pixels)
        circle_cx, circle_cy, circle_r = ImageProcessing.get_circle_location(binary_mask)

        # only consider edges and make them bold
        edges_only = np.array(cv.Canny(single_valued_pixels, 50, 50), dtype=np.float32)
        edges_only_dilated = cv.dilate(
            edges_only, cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
        )

        # blacken the outer 10% of the circle radius
        edges_only_dilated *= ImageProcessing.get_circle_mask(
            edges_only_dilated.shape, circle_r * 0.9, circle_cx, circle_cy
        )

        # determine how many pixels inside the circle are made up of "edge pixels"
        edge_fraction = round((np.sum(edges_only_dilated) / 255) / np.sum(binary_mask), 6)

        # TODO: the values below should be adjusted by looking at the ifgs directly
        status = 1 if (edge_fraction > 0.02) else 0

        logger.debug(f"exposure = {_VBDSD.current_exposure}, edge_fraction = {edge_fraction}")

        if save_image:
            image_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            raw_image_name = f"{image_timestamp}-{status}-raw.jpg"
            processed_image_name = f"{image_timestamp}-{status}-processed.jpg"
            processed_frame = ImageProcessing.add_markings_to_image(
                edges_only_dilated, edge_fraction, circle_cx, circle_cy, circle_r
            )
            cv.imwrite(os.path.join(IMG_DIR, raw_image_name), frame)
            cv.imwrite(os.path.join(IMG_DIR, processed_image_name), processed_frame)

        return status

    @staticmethod
    def run(save_image: bool) -> int:
        # run autoexposure function every 3 minutes
        now = time.time()
        if (now - _VBDSD.last_autoexposure_time) > 180:
            _VBDSD.adjust_exposure()
            _VBDSD.last_autoexposure_time = now

        frame = _VBDSD.take_image()
        return _VBDSD.determine_frame_status(frame, save_image)


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
    def main(shared_queue: queue.Queue, infinite_loop: bool = True, headless: bool = False):
        global logger
        global _CONFIG

        # headless mode = don't use logger, just print messages to console, always save images
        if headless:
            logger = Logger(origin="vbdsd", just_print=True)
        _CONFIG = ConfigInterface.read()

        status_history = RingList(_CONFIG["vbdsd"]["evaluation_size"])
        current_state = None

        repeated_camera_error_count = 0

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
                    _VBDSD.init(_CONFIG["vbdsd"]["camera_id"])

                # reinit if parameter changes
                new_size = _CONFIG["vbdsd"]["evaluation_size"]
                if status_history.maxsize() != new_size:
                    logger.debug(
                        "Size of VBDSD history has changed: "
                        + f"{status_history.maxsize()} -> {new_size}"
                    )
                    status_history.reinitialize(new_size)

                # sleep while sun angle is too low
                if (not headless) and Astronomy.get_current_sun_elevation().is_within_bounds(
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

                # take a picture and process it: status is in [0, 1]
                # a CameraError is allowed to happen 3 times in a row
                # at the 4th time the camera is not able to take an image
                # an Exception will be raised (and VBDSD will be restarted)
                try:
                    status = _VBDSD.run(headless or _CONFIG["vbdsd"]["save_images"])
                    repeated_camera_error_count = 0
                except CameraError as e:
                    repeated_camera_error_count += 1
                    if repeated_camera_error_count > 3:
                        raise e
                    else:
                        logger.debug(
                            f"camera occured ({repeated_camera_error_count} time(s) in a row). "
                            + "sleeping 15 seconds, reconnecting camera"
                        )
                        _VBDSD.deinit()
                        time.sleep(15)
                        continue

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

                logger.error(f"error in VBDSD thread: {repr(e)}")
                logger.info(f"sleeping 30 seconds, reinitializing VBDSD thread")
                time.sleep(30)
