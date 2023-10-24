import os
import threading
import time
import cv2 as cv
import numpy as np
from typing import Any, Optional
import pydantic

import tum_esm_utils
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="helios")

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_AUTOEXPOSURE_IMG_DIR = os.path.join(
    _PROJECT_DIR, "logs", "helios-autoexposure"
)
_CONFIG: Optional[types.Config] = None


class CameraError(Exception):
    pass


class _Helios:
    cam: Optional[Any] = None
    current_exposure = None
    last_autoexposure_time = 0.0
    available_exposures = None

    @staticmethod
    def init(camera_id: int, retries: int = 5) -> None:
        _Helios.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        assert _Helios.cam is not None
        _Helios.cam.release()

        for _ in range(retries):
            _Helios.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            assert _Helios.cam is not None

            if _Helios.cam.isOpened():
                if _Helios.available_exposures is None:
                    _Helios.available_exposures = _Helios.get_available_exposures(
                    )
                    logger.debug(
                        f"determined available exposures: {_Helios.available_exposures}"
                    )
                    assert (
                        len(_Helios.available_exposures) > 0
                    ), "did not find any available exposures"

                _Helios.current_exposure = min(_Helios.available_exposures)
                _Helios.update_camera_settings(
                    exposure=_Helios.current_exposure
                )
                return
            else:
                time.sleep(2)

        raise CameraError("could not initialize camera")

    @staticmethod
    def deinit() -> None:
        """
        Possibly release the camera (linked over cv2.VideoCapture)
        """
        if _Helios.cam is not None:
            _Helios.cam.release()
            _Helios.cam = None

    @staticmethod
    def get_available_exposures() -> list[int]:
        """
        Loop over every integer in [-20, ..., +20] and try to set
        the camera exposure to each value. Return a list of integers
        that the camera accepted as an exposure setting.
        """
        assert _Helios.cam is not None, "camera is not initialized yet"

        possible_values: list[int] = []
        for exposure in range(-20, 20):
            _Helios.cam.set(cv.CAP_PROP_EXPOSURE, exposure)
            if _Helios.cam.get(cv.CAP_PROP_EXPOSURE) == exposure:
                possible_values.append(exposure)

        return possible_values

    @staticmethod
    def update_camera_settings(
        exposure: int,
        brightness: int = 64,
        contrast: int = 64,
        saturation: int = 0,
        gain: int = 0,
        width: int = 1280,
        height: int = 720,
    ) -> None:
        """
        Update the settings of the connected camera. Which settings are
        available depends on the camera model. However, this function will
        throw an AssertionError, when the value could not be changed.
        """
        assert _Helios.cam is not None, "camera is not initialized yet"

        properties = {
            "width": (cv.CAP_PROP_FRAME_WIDTH, width),
            "height": (cv.CAP_PROP_FRAME_HEIGHT, height),
            "exposure": (cv.CAP_PROP_EXPOSURE, exposure),
            "brightness": (cv.CAP_PROP_BRIGHTNESS, brightness),
            "contrast": (cv.CAP_PROP_CONTRAST, contrast),
            "saturation": (cv.CAP_PROP_SATURATION, saturation),
            "gain": (cv.CAP_PROP_GAIN, gain),
        }
        for property_name, (key, value) in properties.items():
            _Helios.cam.set(key, value)
            if property_name not in ["width", "height"]:
                new_value = _Helios.cam.get(key)
                if new_value != value:
                    logger.warning(
                        f"could not set {property_name} to {value}, value is still at {new_value}"
                    )

        # throw away some images after changing settings. I don't know
        # why this is necessary, but it resolves a lot of issues
        for _ in range(2):
            _Helios.cam.read()

    @staticmethod
    def take_image(
        retries: int = 10, trow_away_white_images: bool = True
    ) -> cv.Mat:
        """
        Take an image using the initialized camera. Raises an
        AssertionError if camera has not been set up.

        Retries up to n times (camera can say "not possible")
        and throws away all mostly white images (overexposed)
        except when specified not to (used in autoexposure).
        """
        assert _Helios.cam is not None, "camera is not initialized yet"

        if not _Helios.cam.isOpened():
            raise CameraError("camera is not open")
        for _ in range(retries + 1):
            ret, frame = _Helios.cam.read()
            if ret:
                if trow_away_white_images and np.mean(frame) > 240:
                    # image is mostly white
                    continue
                return frame
        raise CameraError("could not take image")

    @staticmethod
    def adjust_exposure() -> None:
        """This function will loop over all available exposures and
        take one image for each exposure. Then it sets exposure to
        the value where the overall mean pixel value color is closest
        to 50.

        **For every exposure:**

        1. set new exposure
        2. 0.3s sleep
        3. image 1 -> 0.1s sleep -> image 2 -> 0.1s sleep -> image 3
        8. calculate mean color of all 3 images
        9. save images to disk"""

        assert _Helios.available_exposures is not None, "camera is not initialized yet"
        assert _Helios.cam is not None, "camera is not initialized yet"
        assert len(_Helios.available_exposures) > 0

        class ExposureResult(pydantic.BaseModel):
            exposure: int
            means: list[float]

        exposure_results: list[ExposureResult] = []

        for exposure in _Helios.available_exposures:
            # set new exposure and wait 0.3s after setting it
            _Helios.cam.set(cv.CAP_PROP_EXPOSURE, exposure)
            time.sleep(0.2)
            assert (
                _Helios.cam.get(cv.CAP_PROP_EXPOSURE) == exposure
            ), f"could not set exposure to {exposure}"

            # throw away some images after changing settings. I don't know
            # why this is necessary, but it resolves a lot of issues
            for _ in range(3):
                _Helios.cam.read()

            # take 3 images and wait 0.1s before each image
            NUMBER_OF_EXPOSURE_IMAGES = 3
            mean_colors: list[float] = []
            for i in range(NUMBER_OF_EXPOSURE_IMAGES):
                time.sleep(0.1)
                img: Any = _Helios.take_image(trow_away_white_images=False)
                mean_colors.append(round(float(np.mean(img)), 3))
                img = utils.HeliosImageProcessing.add_text_to_image(
                    img, f"mean={mean_colors[-1]}", color=(0, 0, 255)
                )
                cv.imwrite(
                    os.path.join(
                        _AUTOEXPOSURE_IMG_DIR, f"exposure-{exposure}-{i+1}.jpg"
                    ), img
                )

            # calculate mean color of all 3 images
            exposure_results.append(
                ExposureResult(exposure=exposure, means=mean_colors)
            )

        logger.debug(f"exposure results: {exposure_results}")

        means: list[float] = [
            sum(r.means) / NUMBER_OF_EXPOSURE_IMAGES for r in exposure_results
        ]
        for m1, m2 in zip(means[:-1], means[1 :]):
            assert m1 < m2 + 5, "mean colors should increase with increasing exposure"

        assert len(exposure_results) > 0, "no possible exposures found"
        new_exposure = int(
            min(
                exposure_results,
                key=lambda r:
                abs(sum(r.means) / NUMBER_OF_EXPOSURE_IMAGES - 50),
            ).exposure
        )
        _Helios.update_camera_settings(exposure=new_exposure)

        if new_exposure != _Helios.current_exposure:
            logger.info(
                f"changing exposure: {_Helios.current_exposure} -> {new_exposure}"
            )
            _Helios.current_exposure = new_exposure

    @staticmethod
    def run(save_image: bool) -> float:
        """
        Take an image and evaluate the sun conditions.
        Run autoexposure function every 5 minutes.

        Returns the edge fraction
        """
        now = time.time()
        if (now - _Helios.last_autoexposure_time) > 300:
            _Helios.adjust_exposure()
            _Helios.last_autoexposure_time = now

        frame = _Helios.take_image()

        edge_fraction = utils.HeliosImageProcessing.get_edge_fraction(
            frame, save_image
        )
        logger.debug(
            f"exposure = {_Helios.current_exposure}, edge_fraction = {edge_fraction}"
        )

        return edge_fraction


class HeliosThread:
    """Thread for determining the current sun conditions in a
    parallel mainloop.

    "Good" sun conditions with respect to EM27 measurements
    means direct sunlight, i.e. no clouds in front of the
    sun. Interferograms recored in diffuse light conditions
    result in a concentration timeseries (after retrieval)
    with a very large standard deviation.

    Direct sunlight can be determined by "hard" shadows, i.e.
    quick transitions between light and dark surfaces. This
    thread periodically takes images in a special camera setup
    and uses edge detected to determine how many hard shadows
    it can find in the image.

    The result of this constant sunlight evaluation is written
    to the StateInterface.
    """
    def __init__(self, config: types.Config) -> None:
        self.__thread = threading.Thread(target=HeliosThread.main)
        self.__logger: utils.Logger = utils.Logger(origin="helios")
        self.config: types.Config = config
        self.is_initialized = False

    def update_thread_state(self, new_config: types.Config) -> None:
        """
        Make sure that the thread loop is (not) running,
        based on config.upload
        """
        self.config = new_config
        should_be_running = HeliosThread.should_be_running(self.config)

        if should_be_running and (not self.is_initialized):
            self.__logger.info("Starting the thread")
            self.is_initialized = True
            self.__thread.start()

        # set up a new thread instance for the next time the thread should start
        if self.is_initialized:
            if self.__thread.is_alive():
                self.__logger.debug("Thread is alive")
            else:
                self.__logger.debug("Thread is not alive, running teardown")
                self.__thread.join()
                self.__thread = threading.Thread(target=HeliosThread.main)
                self.is_initialized = False

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Should the thread be running? (based on config.upload)"""
        return ((not config.general.test_mode) and
                (config.helios is not None) and
                (config.measurement_triggers.consider_helios))

    @staticmethod
    def main(headless: bool = False) -> None:
        """
        Main entrypoint of the thread.

        headless mode = don't write to log files, print to console, save all images
        """
        global logger
        global _CONFIG

        if headless:
            logger = utils.Logger(origin="helios", just_print=True)
        _CONFIG = types.Config.load()

        # Check for termination
        if ((_CONFIG.helios is None) or
            (not HeliosThread.should_be_running(_CONFIG))):
            return

        # a list storing the last n calculated edge fractions
        edge_fraction_history = tum_esm_utils.datastructures.RingList(
            max_size=_CONFIG.helios.evaluation_size
        )
        current_state: Optional[bool] = None

        repeated_camera_error_count = 0

        while True:
            start_time = time.time()
            _CONFIG = types.Config.load()

            # Check for termination
            if ((_CONFIG.helios is None) or
                (not HeliosThread.should_be_running(_CONFIG))):
                return

            try:
                # init camera connection
                if _Helios.cam is None:
                    logger.info(f"Initializing Helios camera")
                    _Helios.init(_CONFIG.helios.camera_id)

                # reinit if parameter changes
                current_max_history_size = edge_fraction_history.get_max_size()
                new_max_history_size = _CONFIG.helios.evaluation_size
                if current_max_history_size != new_max_history_size:
                    logger.debug(
                        "Size of Helios history has changed: " +
                        f"{current_max_history_size} -> {new_max_history_size}"
                    )
                    edge_fraction_history.set_max_size(new_max_history_size)

                # sleep while sun angle is too low
                current_sun_elevation = utils.Astronomy.get_current_sun_elevation(
                    _CONFIG
                )
                min_sun_elevation = _CONFIG.general.min_sun_elevation
                helios_should_be_running = headless or (
                    current_sun_elevation > min_sun_elevation
                )
                if not helios_should_be_running:
                    logger.debug(
                        "Current sun elevation below minimum: Waiting 5 minutes"
                    )
                    if current_state is not None:
                        interfaces.StateInterface.update_state(
                            helios_indicates_good_conditions="no"
                        )
                        current_state = None
                        # reinit for next day
                        _Helios.deinit()
                    time.sleep(300)
                    continue

                # take a picture and process it: status is in [0, 1]
                # a CameraError is allowed to happen 3 times in a row
                # at the 4th time the camera is not able to take an image
                # an Exception will be raised (and Helios will be restarted)
                try:
                    new_edge_fraction = _Helios.run(
                        headless or _CONFIG.helios.save_images
                    )
                    repeated_camera_error_count = 0
                except CameraError as e:
                    repeated_camera_error_count += 1
                    if repeated_camera_error_count > 3:
                        raise e
                    else:
                        logger.debug(
                            f"camera occured ({repeated_camera_error_count} time(s) in a row). "
                            + "sleeping 15 seconds, reinitializing Helios"
                        )
                        _Helios.deinit()
                        time.sleep(15)
                        continue

                # append sun status to status history
                edge_fraction_history.append(new_edge_fraction)
                logger.debug(
                    f"New Helios edge_fraction: {new_edge_fraction}. " +
                    f"Current history: {edge_fraction_history.get()}"
                )

                # evaluate sun state only if list is filled
                new_state: Optional[bool] = current_state
                if edge_fraction_history.is_full():
                    average_edge_fraction = float(
                        edge_fraction_history.sum() /
                        edge_fraction_history.get_max_size()
                    )

                    # eliminating quickly alternating decisions
                    # see https://github.com/tum-esm/pyra/issues/148

                    upper_ef_threshold = _CONFIG.helios.edge_detection_threshold
                    lower_ef_threshold = upper_ef_threshold * 0.7
                    if current_state is None:
                        new_state = average_edge_fraction >= upper_ef_threshold
                    else:
                        # if already running and below lower threshold -> stop
                        if current_state and (
                            average_edge_fraction <= lower_ef_threshold
                        ):
                            new_state = False

                        # if not running and above upper threshold -> start
                        if (not current_state
                           ) and (average_edge_fraction >= upper_ef_threshold):
                            new_state = True

                logger.debug(
                    f"State: {'GOOD' if (new_state == True) else 'BAD'}"
                )

                if current_state != new_state:
                    logger.info(
                        f"State change: {'BAD -> GOOD' if (new_state == True) else 'GOOD -> BAD'}"
                    )

                    interfaces.StateInterface.update_state(
                        helios_indicates_good_conditions=(
                            "inconclusive" if (
                                new_state is None
                            ) else "yes" if new_state else "no"
                        )
                    )
                    current_state = new_state

                # wait rest of loop time
                elapsed_time = time.time() - start_time
                time_to_wait = _CONFIG.helios.seconds_per_interval - elapsed_time
                if time_to_wait > 0:
                    logger.debug(
                        f"Finished iteration, waiting {round(time_to_wait, 2)} second(s)."
                    )
                    time.sleep(time_to_wait)

            except Exception as e:
                edge_fraction_history.clear()
                _Helios.deinit()

                logger.error(f"error in HeliosThread: {repr(e)}")
                logger.exception(e)
                logger.info(f"sleeping 30 seconds, reinitializing HeliosThread")
                time.sleep(30)
