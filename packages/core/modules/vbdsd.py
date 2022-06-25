# filename          : vbdsd.py
# description  : Vision-Based Direct Sunlight Detector
# ==============================================================================
# author            : Benno Voggenreiter
# email             : -
# date              : 20190719
# version           : 1.0
# notes             : Created by Benno Voggenreiter (Master's Thesis)
# license           : -
# py version        : 2.7
# ==============================================================================
# author            : Benno Voggenreiter
# email             : -
# date              : 20210226
# version           : 2.0
# notes             : Improved by Nikolas Hars (Bachelor's Thesis)
# license           : -
# py version        : 2.7
# ==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220328
# version           : 3.0
# notes             : Upgrade to Python 3.10 and refactoring for Pyra 4.
# license           : -
# py version        : 3.10
# ==============================================================================


import multiprocessing
import os
import signal
import shutil
import time
import astropy.units as astropy_units
import cv2 as cv
import numpy as np
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
    RingList,
    Astronomy,
)

logger = Logger(origin="pyra.core.vbdsd")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
IMG_DIR = os.path.join(PROJECT_DIR, "runtime-data", "vbdsd")
_CONFIG = None


class _VBDSD:
    cam = None

    @staticmethod
    def init_cam(retries: int = 5):
        """
        init_cam(int id): Connects to the camera with id and sets its parameters.
        If successfully connected, the function returns an instance object of the
        camera, otherwise None will be returned.
        """
        camera_id = _CONFIG["vbdsd"]["camera_id"]
        
        _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        _VBDSD.cam.release()

        for _ in range(retries):
            _VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            time.sleep(1)
            if _VBDSD.cam.isOpened():
                logger.debug(f"Camera with id {camera_id} is now connected")
                _VBDSD.cam.set(3, 1280)  # width
                _VBDSD.cam.set(4, 720)  # height
                _VBDSD.cam.set(15, -12)  # exposure
                _VBDSD.cam.set(10, 64)  # brightness
                _VBDSD.cam.set(11, 64)  # contrast
                _VBDSD.cam.set(12, 0)  # saturation
                _VBDSD.cam.set(14, 0)  # gain
                _VBDSD.cam.read()
                _VBDSD.change_exposure()
                return
        
        logger.warning(f"Camera with id {camera_id} could not be found")
        

    @staticmethod
    def eval_sun_state(frame):
        """
        This function will extract the current sun state from an input image (frame)
        Is uses cv2 package for image detection / computer vision tasks.

        returns:
        1, frame -> sun status is good, picture used for evaluation
        0, frame -> sun status is bad, picture used for evaluation
        """
        blur = cv.medianBlur(frame, 15)
        frame_gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

        if frame_gray.shape[1] == 1280:  # Crop on sides
            frame_gray = frame_gray[:, 170:1100]
            frame = frame[:, 170:1100]

        img_b = cv.adaptiveThreshold(
            frame_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 23, 2
        )
        img_b = cv.medianBlur(img_b, 9)
        img_b, frame = _VBDSD.extend_border(img_b, frame)

        circles = cv.HoughCircles(
            img_b,
            cv.HOUGH_GRADIENT,
            1,
            900,
            param1=200,
            param2=1,
            minRadius=345,
            maxRadius=355,
        )
        # (min + max) radius have to be quite exact.
        # 900 = Distance to next circle to prevent wrong circles

        if circles is None:
            return -1, frame

        circles = np.uint16(np.around(circles))

        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            cv.circle(img_b, center, radius - 10, 255, 30)
            cv.circle(img_b, center, radius - 20, 0, 15)
            cv.circle(frame, center, radius, 255, 5)

        contours, hierarchy = cv.findContours(
            img_b.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE
        )

        ppi_contour = None
        ppi = -1
        areas = [0]
        if len(contours) > 0:
            for i in range(len(contours)):
                if cv.contourArea(contours[i]) > 2000:
                    x, y, w, h = cv.boundingRect(contours[i])
                    if float(w) == float(
                        h
                    ):  # Use constraints to find the projection plane
                        ppi_contour = contours[i]  # Save contour
                        ppi = i

            if ppi_contour is None:
                return -1, frame

            if ppi >= 0:
                c_areas = []
                for contour in contours:
                    temp_area = cv.contourArea(contour)
                    c_areas.append(temp_area)
                indices = np.argsort(c_areas)

            font = cv.FONT_HERSHEY_SIMPLEX
            color = (0, 0, 255)  # red

            # x_length = frame.shape[1]
            y_length = frame.shape[0]

            # Check the size and parents and level of contour
            for i in indices:
                if hierarchy[0][i][3] == ppi:  # Contour is on pp
                    x, y, w, h = cv.boundingRect(contours[i])
                    pos = (x, y)
                    cv.drawContours(frame, contours[i], -1, color, 4)
                    cv.putText(frame, ("%s" % (i)), pos, font, 1, color, 2, 10)
                    areas.append(c_areas[i])

        cv.putText(
            frame,
            "%05d" % (np.sum(areas)),
            (10, y_length - 20),
            font,
            1,
            (255, 255, 255),
            2,
            10,
        )

        if np.sum(areas) >= 8000:
            return 1, frame
        else:
            return 0, frame

    @staticmethod
    def extend_border(img, frame):
        """This function allows to use different models of the vbdsd hardware setup
        by cutting the field of view to the same base.
        """
        bordersize = 50
        make_border = lambda f: cv.copyMakeBorder(
            f,
            top=bordersize,
            bottom=bordersize,
            left=0,
            right=0,
            borderType=cv.BORDER_CONSTANT,
            value=[0, 0, 0],
        )
        return make_border(img), make_border(frame)

    @staticmethod
    def change_exposure(diff=0):
        """Changes the camera exposure settings according to the current sun angle
        with a known setting. Allows to add an INT on top for further adjustment.
        """

        current_sun_angle = Astronomy.get_current_sun_elevation()

        if current_sun_angle < 4 * astropy_units.deg:
            exp = -9 + diff
        elif current_sun_angle < 6 * astropy_units.deg:
            exp = -10 + diff
        elif current_sun_angle < 10 * astropy_units.deg:
            exp = -11 + diff
        else:
            exp = -12 + diff

        _VBDSD.cam.set(15, exp)
        _VBDSD.cam.read()
        time.sleep(0.2)

    @staticmethod
    def run(retries: int = 5):
        """
        Calls take_vbdsd_image and processes the image if successful.

        Returns
        status: 1 or 0
        frame: Source image
        """

        frame = None
        for _ in range(retries + 1):
            ret, frame = _VBDSD.cam.read()
            if ret:
                return _VBDSD.eval_sun_state(frame)

        return 0, frame


class VBDSD_Thread:
    def __init__(self):
        self.__process = None

    def start(self):
        """
        Start a thread using the multiprocessing library
        """
        logger.info("Starting thread")
        self.__process = multiprocessing.Process(target=VBDSD_Thread.main)
        self.__process.start()

    def is_running(self):
        return self.__process is not None

    def stop(self):
        """
        Stop the thread, remove all images inside the directory
        "runtime_data/vbdsd" and set the state to 'null'
        """

        logger.info("Terminating thread")
        self.__process.terminate()

        logger.debug("Removing all images")
        VBDSD_Thread.__remove_vbdsd_images()

        logger.debug('Setting state to "null"')
        StateInterface.update({"vbdsd_indicates_good_conditions": None})

        self.__process = None

    @staticmethod
    def __remove_vbdsd_images():
        if os.path.exists(IMG_DIR):
            shutil.rmtree(IMG_DIR)
        os.mkdir(IMG_DIR)

    @staticmethod
    def main(infinite_loop=True):
        global _CONFIG
        _CONFIG = ConfigInterface.read()
        #delete all temp pictures when vbdsd is deactivated
        if _CONFIG["vbdsd"] is None:
            VBDSD_Thread.__remove_vbdsd_images()
            return

        status_history = RingList(_CONFIG["vbdsd"]["evaluation_size"])
        current_state = None

        while True:
            start_time = time.time()
            _CONFIG = ConfigInterface.read()
            # delete all temp pictures when vbdsd is deactivated
            if _CONFIG["vbdsd"] is None:
                VBDSD_Thread.__remove_vbdsd_images()
                return

            #init camera connection
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
                None, _CONFIG["vbdsd"]["min_sun_elevation"] * astropy_units.deg
            ):
                logger.debug("Current sun elevation below minimum: Waiting 5 minutes")
                if current_state != None:
                    StateInterface.update(
                        {"vbdsd_indicates_good_conditions": current_state}
                    )
                    current_state = None
                time.sleep(300)
                continue

            # take a picture and process it
            status, frame = _VBDSD.run()

            # retry with change_exposure(1) if status fail
            if status == -1:
                _VBDSD.change_exposure(1)
                status, frame = _VBDSD.run()

            # append sun status to status history
            status_history.append(max(status, 0))
            logger.debug(f"New VBDSD status: {status}")
            logger.debug(f"New VBDSD status history: {status_history.get()}")

            if frame is not None:
                img_name = time.strftime("%H_%M_%S_") + str(status) + ".jpg"
                img_path = os.path.join(IMG_DIR, img_name)
                cv.imwrite(img_path, frame)
                logger.debug(f"Saving image to: {img_path}")
            else:
                logger.debug(f"Could not take image")

            # evaluate sun state only if list is filled
            if status_history.size() == status_history.maxsize():
                score = status_history.sum() / status_history.size()
                new_state = score > _CONFIG["vbdsd"]["measurement_threshold"]
            else:
                new_state = None

            if current_state != new_state:
                logger.info(
                    f"State change: {'GOOD' if current_state else 'BAD'}"
                    + f" -> {'GOOD' if new_state else 'BAD'}"
                )
                StateInterface.update({"vbdsd_indicates_good_conditions": new_state})
                current_state = new_state

            # wait rest of loop time
            elapsed_time = time.time() - start_time
            time_to_wait = _CONFIG["vbdsd"]["seconds_per_interval"] - elapsed_time
            if time_to_wait > 0:
                logger.debug(
                    f"Finished iteration, waiting {round(time_to_wait, 2)} second(s)"
                )
                time.sleep(time_to_wait)

            if not infinite_loop:
                return status_history
