import datetime
from typing import Any, Optional
import os
import threading
import time
import cv2 as cv
import numpy as np
import pydantic
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import types, utils, interfaces

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_AUTOEXPOSURE_IMG_DIR = os.path.join(
    _PROJECT_DIR, "logs", "helios-autoexposure"
)
_NUMBER_OF_EXPOSURE_IMAGES = 3


class CameraError(Exception):
    pass


class HeliosInterface:
    def __init__(
        self,
        logger: utils.Logger,
        camera_id: int,
        initialization_tries: int = 5,
    ) -> None:
        self.logger = logger
        self.camera: cv.VideoCapture = cv.VideoCapture(camera_id, cv.CAP_DSHOW)

        self.camera.release()

        for _ in range(initialization_tries):
            self.camera = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            if self.camera.isOpened():
                available_exposures = self.get_available_exposures()
                logger.debug(
                    f"determined available exposures: {available_exposures}"
                )
                if len(available_exposures) == 0:
                    raise CameraError("did not find any available exposures")

                self.current_exposure: int = min(available_exposures)
                self.last_autoexposure_time: float = 0.0
                self.target_pixel_brightness: int = 0
                self.available_exposures: list[int] = available_exposures

                self.update_camera_settings(exposure=self.current_exposure)
                return
            else:
                logger.debug(f"could not open camera, retrying in 2 seconds")
                time.sleep(2)

        raise CameraError(
            f"could not initialize camera in {initialization_tries} tries"
        )

    def __del__(self) -> None:
        """Release the camera"""

        if self.camera is not None:
            self.camera.release()

    def get_available_exposures(self) -> list[int]:
        """Loop over every integer in [-20, ..., +20] and try to set
        the camera exposure to each value. Return a list of integers
        that the camera accepted as an exposure setting."""

        possible_values: list[int] = []
        for exposure in range(-20, 20):
            self.camera.set(cv.CAP_PROP_EXPOSURE, exposure)
            if self.camera.get(cv.CAP_PROP_EXPOSURE) == exposure:
                possible_values.append(exposure)

        return possible_values

    def update_camera_settings(
        self,
        exposure: int,
        brightness: int = 64,
        contrast: int = 64,
        saturation: int = 0,
        gain: int = 0,
        width: int = 1280,
        height: int = 720,
    ) -> None:
        """Update the settings of the connected camera. Which settings are
        available depends on the camera model. However, this function will
        throw an AssertionError, when the value could not be changed."""

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
            self.camera.set(key, value)
            if property_name not in ["width", "height"]:
                new_value = self.camera.get(key)
                if new_value != value:
                    self.logger.warning(
                        f"could not set {property_name} to {value}, value is still at {new_value}"
                    )

        # throw away some images after changing settings. I don't know
        # why this is necessary, but it resolves a lot of issues
        for _ in range(2):
            self.camera.read()

    def take_image(
        self,
        retries: int = 10,
        trow_away_white_images: bool = True,
    ) -> np.ndarray[Any, Any]:
        """Take an image using the initialized camera. Raises an
        AssertionError if camera has not been set up.

        Retries up to n times (camera can say "not possible")
        and throws away all mostly white images (overexposed)
        except when specified not to (used in autoexposure)."""

        if not self.camera.isOpened():
            raise CameraError("camera is not open")
        for _ in range(retries + 1):
            ret, frame = self.camera.read()
            if ret:
                if trow_away_white_images and np.mean(
                    frame  # type: ignore
                ) > 240:
                    # image is mostly white
                    continue
                return np.array(frame)
        raise CameraError("could not take image")

    def adjust_exposure(self) -> None:
        """This function will loop over all available exposures and
        take one image for each exposure. Then it sets exposure to
        the value where the overall mean pixel value color is closest
        to `self.target_pixel_brightness`.

        **For every exposure:**

        1. set new exposure
        2. 0.3s sleep
        3. image 1 -> 0.1s sleep -> image 2 -> 0.1s sleep -> image 3
        8. calculate mean color of all 3 images
        9. save images to disk"""
        class ExposureResult(pydantic.BaseModel):
            exposure: int
            means: list[float]

        exposure_results: list[ExposureResult] = []

        for exposure in self.available_exposures:
            # set new exposure and wait 0.3s after setting it
            self.camera.set(cv.CAP_PROP_EXPOSURE, exposure)
            time.sleep(0.2)
            assert (
                self.camera.get(cv.CAP_PROP_EXPOSURE) == exposure
            ), f"could not set exposure to {exposure}"

            # throw away some images after changing settings. I don't know
            # why this is necessary, but it resolves a lot of issues
            for _ in range(3):
                self.camera.read()

            # take 3 images and wait 0.1s before each image
            mean_colors: list[float] = []
            for i in range(_NUMBER_OF_EXPOSURE_IMAGES):
                time.sleep(0.1)
                img: Any = self.take_image(trow_away_white_images=False)
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

        self.logger.debug(f"exposure results: {exposure_results}")
        means: list[float] = [
            sum(r.means) / _NUMBER_OF_EXPOSURE_IMAGES for r in exposure_results
        ]
        for m1, m2 in zip(means[:-1], means[1 :]):
            assert m1 < m2 + 5, "mean colors should increase with increasing exposure"

        assert len(exposure_results) > 0, "no possible exposures found"
        new_exposure = int(
            min(
                exposure_results,
                key=lambda r: abs((sum(r.means) / _NUMBER_OF_EXPOSURE_IMAGES) -
                                  self.target_pixel_brightness),
            ).exposure
        )
        self.update_camera_settings(exposure=new_exposure)

        if new_exposure != self.current_exposure:
            self.logger.info(
                f"changing exposure: {self.current_exposure} -> {new_exposure}"
            )
            self.current_exposure = new_exposure

    def run(
        self,
        station_id: str,
        edge_color_threshold: int,
        target_pixel_brightness: int,
        save_images_to_archive: bool,
        save_current_image: bool,
    ) -> float:
        """Take an image and evaluate the sun conditions. Run autoexposure
        function every 5 minutes. Returns the edge fraction."""
        perform_autoexposure: bool = False
        now = time.time()
        if (now - self.last_autoexposure_time) > 300:
            self.logger.debug("performing autoexposure after 5 minutes")
            perform_autoexposure = True
        if self.target_pixel_brightness != target_pixel_brightness:
            self.logger.debug(
                "performing autoexposure because target_pixel_brightness changed"
                +
                f" ({self.target_pixel_brightness} -> {target_pixel_brightness})"
            )
            perform_autoexposure = True
        if perform_autoexposure:
            self.target_pixel_brightness = target_pixel_brightness
            self.last_autoexposure_time = now
            self.adjust_exposure()

        frame = self.take_image()

        edge_fraction = utils.HeliosImageProcessing.get_edge_fraction(
            frame=frame,
            station_id=station_id,
            edge_color_threshold=edge_color_threshold,
            save_images_to_archive=save_images_to_archive,
            save_current_image=save_current_image,
        )
        self.logger.debug(
            f"exposure = {self.current_exposure}, edge_fraction = {edge_fraction}"
        )

        return edge_fraction


class HeliosThread(AbstractThread):
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
    to the StateInterface."""
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return ((config.helios is not None) and
                (not config.general.test_mode) and
                (config.measurement_triggers.consider_helios))

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=HeliosThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        logger = utils.Logger(origin="helios", just_print=headless)
        config = types.Config.load()
        assert config.helios is not None, "This is a bug in Pyra"
        helios_instance: Optional[HeliosInterface] = None

        # a list storing the last n calculated edge fractions
        edge_fraction_history = tum_esm_utils.datastructures.RingList(
            max_size=config.helios.evaluation_size
        )
        current_state: Optional[bool] = None
        last_state_change: Optional[datetime.datetime] = None

        # how many cycles (initialization + mainloop) have been run
        # without successfully fetching an image from the camera
        repeated_camera_error_count: int = 0

        while True:
            start_time = time.time()
            config = types.Config.load()

            try:
                # Check for termination
                if not HeliosThread.should_be_running(config):
                    if helios_instance is not None:
                        logger.info("Helios thread has been terminated")
                        del helios_instance
                        helios_instance = None
                    return
                assert config.helios is not None, "This is a bug in Pyra"

                # sleep while sun angle is too low
                current_sun_elevation = utils.Astronomy.get_current_sun_elevation(
                    config
                )
                min_sun_elevation = config.general.min_sun_elevation
                if current_sun_elevation < min_sun_elevation:
                    logger.debug(
                        "Current sun elevation below minimum, sleeping 5 minutes"
                    )
                    interfaces.StateInterface.update_state(
                        helios_indicates_good_conditions="no"
                    )
                    if helios_instance is not None:
                        del helios_instance
                        helios_instance = None
                    time.sleep(300)
                    continue

                # initialize HeliosInterface if necessary
                if helios_instance is None:
                    try:
                        helios_instance = HeliosInterface(
                            logger, config.helios.camera_id
                        )
                    except CameraError as e:
                        logger.error(
                            f"could not initialize HeliosInterface: {repr(e)}"
                        )
                        logger.exception(e)
                        logger.info(
                            f"sleeping 30 seconds, reinitializing HeliosInterface"
                        )
                        time.sleep(30)
                        continue

                # reinit evaluation history if size changes
                current_max_history_size = edge_fraction_history.get_max_size()
                new_max_history_size = config.helios.evaluation_size
                if current_max_history_size != new_max_history_size:
                    logger.debug(
                        "Size of Helios history has changed: " +
                        f"{current_max_history_size} -> {new_max_history_size}"
                    )
                    edge_fraction_history.set_max_size(new_max_history_size)

                # take a picture and process it: status is in [0, 1]
                # a CameraError is allowed to happen 3 times in a row
                # at the 4th time the camera is not able to take an image
                # an Exception will be raised (and Helios will be restarted)
                try:
                    new_edge_fraction = helios_instance.run(
                        station_id=config.general.station_id,
                        edge_color_threshold=config.helios.edge_color_threshold,
                        target_pixel_brightness=config.helios.
                        target_pixel_brightness,
                        save_images_to_archive=(
                            config.helios.save_images_to_archive
                        ),
                        save_current_image=(config.helios.save_current_image),
                    )
                    repeated_camera_error_count = 0
                except CameraError as e:
                    repeated_camera_error_count += 1
                    if repeated_camera_error_count > 3:
                        raise e
                    else:
                        logger.debug(
                            f"camera occured ({repeated_camera_error_count} time(s) in a row). "
                            + "sleeping 30 seconds, reinitializing Helios"
                        )
                        del helios_instance
                        helios_instance = None
                        time.sleep(30)
                        continue

                # append sun status to status history
                edge_fraction_history.append(new_edge_fraction)
                logger.debug(
                    f"New Helios edge_fraction: {new_edge_fraction}. " +
                    f"Current history: {edge_fraction_history.get()}"
                )

                # evaluate sun state only if list is filled
                if edge_fraction_history.is_full():
                    new_state: Optional[bool] = current_state

                    average_edge_fraction = float(
                        edge_fraction_history.sum() /
                        edge_fraction_history.get_max_size()
                    )

                    # eliminating quickly alternating decisions
                    # see https://github.com/tum-esm/pyra/issues/148

                    upper_ef_threshold = config.helios.edge_pixel_threshold / 100.0
                    lower_ef_threshold = upper_ef_threshold * 0.7
                    if new_state is None:
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

                    logger.debug(f"New state: {'GOOD' if new_state else 'BAD'}")
                    if current_state == new_state:
                        logger.debug("State did not change")
                        interfaces.StateInterface.update_state(
                            helios_indicates_good_conditions={ # type: ignore
                                None: "inconclusive",
                                True: "yes",
                                False: "no",
                            }[current_state]
                        )
                    else:
                        logger.debug("State changed")

                        # only do state change if last_state_change is long ago in
                        # the past see https://github.com/tum-esm/pyra/issues/195

                        update_state_file = last_state_change is None or (
                            (datetime.datetime.now() -
                             last_state_change).total_seconds()
                            >= config.helios.min_seconds_between_state_changes
                        )
                        if update_state_file:
                            logger.info(
                                f"State change: " + {
                                    True: "GOOD",
                                    False: "BAD",
                                    None: "None",
                                }[current_state] + " -> " + {
                                    True: "GOOD",
                                    False: "BAD",
                                }[new_state]
                            )
                            interfaces.StateInterface.update_state(
                                helios_indicates_good_conditions={ # type: ignore
                                    None: "inconclusive",
                                    True: "yes",
                                    False: "no",
                                }[new_state]
                            )
                            current_state = new_state
                            last_state_change = datetime.datetime.now()
                        else:
                            logger.debug(
                                "Not updating state file because last change was too recent"
                            )
                else:
                    logger.debug(
                        "Not evaluating sun state because " +
                        "Helios buffer is still filling up"
                    )

                # wait rest of loop time
                elapsed_time = time.time() - start_time
                time_to_wait = config.helios.seconds_per_interval - elapsed_time
                if time_to_wait > 0:
                    logger.debug(
                        f"Finished iteration, waiting {round(time_to_wait, 2)} second(s)."
                    )
                    time.sleep(time_to_wait)

            except Exception as e:
                edge_fraction_history.clear()
                del helios_instance
                helios_instance = None

                logger.error(f"error in HeliosThread: {repr(e)}")
                logger.exception(e)
                logger.info(f"sleeping 30 seconds, reinitializing HeliosThread")
                time.sleep(30)
