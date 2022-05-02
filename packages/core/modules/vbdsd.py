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


# TODO: Use logging after initial tests
import os
import time
import astropy
import cv2 as cv
from filelock import FileLock
import numpy as np
import json

from packages.core.utils.validation import Validation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"

from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.vbdsd")


class RingList:
    """Base code created by Flavio Catalani on Tue, 5 Jul 2005 (PSF).
    Added sum() and reinitialize() functions.
    """

    def __init__(self, length):
        self.__data__ = []
        self.__full__ = 0
        self.__max__ = length
        self.__cur__ = 0

    def append(self, x):
        if self.__full__ == 1:
            for i in range(0, self.__cur__ - 1):
                self.__data__[i] = self.__data__[i + 1]
            self.__data__[self.__cur__ - 1] = x
        else:
            self.__data__.append(x)
            self.__cur__ += 1
            if self.__cur__ == self.__max__:
                self.__full__ = 1

    def get(self):
        return self.__data__

    def remove(self):
        if self.__cur__ > 0:
            del self.__data__[self.__cur__ - 1]
            self.__cur__ -= 1

    def size(self):
        return self.__cur__

    def maxsize(self):
        return self.__max__

    def sum(self):
        return float(sum(self.get()))

    def reinitialize(self, length):
        self.__max__ = length
        self.__full__ = 0
        self.__cur__ = 0
        handover_list = self.get()
        self.__data__ = []

        for item in handover_list:
            self.append(item)

    def __str__(self):
        return "".join(self.__data__)


def read_json_config_files():
    """Reads and validates the available json config files.

    Returns
    SETUP:dict and PARAMS:dict as Tuple
    """
    # TODO: Handle errors from config validation
    with FileLock(CONFIG_LOCK_PATH):
        Validation.check_parameters_config()
        Validation.check_setup_config()
        with open(SETUP_FILE_PATH, "r") as f:
            SETUP = json.load(f)
        with open(PARAMS_FILE_PATH, "r") as f:
            PARAMS = json.load(f)

    return (SETUP, PARAMS)


def init_cam(cam_id):
    """init_cam(int id): Connects to the camera with id and sets its parameters.
    If successfully connected, the function returns an instance object of the
    camera, otherwise None will be returned.
    """
    height = 720  # 768
    width = 1280  # 1024

    cam = cv.VideoCapture(cam_id)
    cam.release()

    for _ in range(5):
        cam = cv.VideoCapture(cam_id)
        time.sleep(1)
        if cam.isOpened():
            cam.set(3, width)
            cam.set(4, height)
            cam.set(15, -12)  # exposure
            cam.set(10, 64)  # brightness
            cam.set(11, 64)  # contrast
            cam.set(12, 0)  # saturation
            cam.set(14, 0)  # gain
            cam.read()
            return cam
    else:
        return None


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

    img_b, frame, border = extend_border(img_b, frame)

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
                if float(w) == float(h):  # Use constraints to find the projection plane
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


def calc_sun_angle_deg(loc):
    """calc_sun_angle_deg(location loc): Computes and returns the current sun
    angle in degree, based on the location loc, computed by get_tracker_position(),
     and current time. Therefore, the pack- ages time and astrophy are required.
    """
    now = astropy.time.now()
    altaz = astropy.coordinates.AltAz(location=loc, obstime=now)
    sun = astropy.coordinates.get_sun(now)
    sun_angle_deg = sun.transform_to(altaz).alt
    return sun_angle_deg


def read_camtracker_config() -> list:
    """Reads the config.txt file of the CamTracker application to receive the
    latest tracker position.

    Returns
    tracker_position as a python list
    """

    target = SETUP["camtracker"]["config_path"]

    if not os.path.isfile(target):
        pass
        # TODO: Raise error?

    f = open(target, "r")

    list_lines = f.readlines()
    first_line = list_lines[0]

    # find $1 and $2 markers
    for n, line in enumerate(list_lines):
        if line == "$1\n":
            line_info1 = n

    # pos1 = latitude,
    # pos2 = longitude,
    # pos3 = height
    tracker_position = [
        list_lines[line_info1 + 1].replace("\n", ""),
        list_lines[line_info1 + 2].replace("\n", ""),
        list_lines[line_info1 + 3].replace("\n", ""),
    ]

    f.close()

    return tracker_position


def get_tracker_position():
    """get_tracker_position(): Reads out the height, the longitude and the
    latitude of the system from CamTrackerConfig.txt, and computes the location
    on earth. Therefore, the python package astropy [23] is imported, and its
    function coord.EarthLocation() is used. The read out parameters, as well as
    the computed location will be returned.
    """

    readout = read_camtracker_config()

    latitude = readout[0] * astropy.units.deg
    longitude = readout[1] * astropy.units.deg
    height = readout[2] * astropy.units.km

    loc = astropy.coordinates.EarthLocation(lon=longitude, lat=latitude, height=height)

    return loc


def extend_border(img, frame):
    """This function allows to use different models of the vbdsd hardware setup
    by cutting the field of view to the same base.
    """
    bordersize = 50  # Extend borders
    img_b = cv.copyMakeBorder(
        img,
        top=bordersize,
        bottom=bordersize,
        left=0,
        right=0,
        borderType=cv.BORDER_CONSTANT,
        value=[0, 0, 0],
    )

    frame = cv.copyMakeBorder(
        frame,
        top=bordersize,
        bottom=bordersize,
        left=0,
        right=0,
        borderType=cv.BORDER_CONSTANT,
        value=[0, 0, 0],
    )
    return img_b, frame, bordersize


def change_exposure(diff=0):
    """Changes the camera exposure settings according to the current sun angle
    with a known setting. Allows to add an INT on top for further adjustment.
    """

    loc = get_tracker_position()
    sun_angle_deg = calc_sun_angle_deg(loc)

    if sun_angle_deg < 4 * astropy.units.deg:
        exp = -9 + diff
    elif sun_angle_deg < 6 * astropy.units.deg:
        exp = -10 + diff
    elif sun_angle_deg < 10 * astropy.units.deg:
        exp = -11 + diff
    else:
        exp = -12 + diff

    cam.set(15, exp)
    cam.read()
    time.sleep(0.2)


def take_vbdsd_image(count: int = 1):
    """Takes a VBDSD image with retry option.

    Returns
    ret(retrieval): 1 or 0
    frame: Source image
    """

    for _ in count:
        ret, frame = cam.read()
        if ret:
            return ret, frame

    return False, None


def process_vbdsd_vision():
    """Calls take_vbdsd_image and processes the image if successful.

    Returns
    status: 1 or 0
    frame: Source image
    """

    ret, frame = take_vbdsd_image(5)
    if ret:
        return eval_sun_state(frame)

    return 0, frame


if __name__ == "__main__":

    SETUP, PARAMS = read_json_config_files()
    status_history = RingList(PARAMS["vbdsd"]["evaluation_size"])

    loc = get_tracker_position()

    cam = init_cam(SETUP["vbdsd"]["cam_id"])
    change_exposure()

    while 1:
        start_time = time.time()
        SETUP, PARAMS = read_json_config_files()

        # sleep while sun angle is too low
        while calc_sun_angle_deg(loc) < PARAMS["vbdsd"]["min_sun_angle"]:
            time.sleep(60)

        # reinit if parameter changes
        if status_history.maxsize() != PARAMS["vbdsd"]["evaluation_size"]:
            status_history.reinitialize(PARAMS["vbdsd"]["evaluation_size"])

        # take a picture and process it
        status, frame = process_vbdsd_vision()
        # retry with change_exposure(1) if status fail
        if status == -1:
            change_exposure(1)
            status, frame = process_vbdsd_vision()

        # append sun status to status history
        if status == 1:
            status_history.append(1)
        else:
            status_history.append(0)

        if os.path.exists(SETUP["vbdsd"]["image_storage_path"]):
            img_name = time.strftime("%H_%M_%S_") + str(status) + ".jpg"
            img_full_path = os.path.join(
                SETUP["vbdsd"]["image_storage_path"] + img_name
            )
            # save image
            cv.imwrite(img_full_path)

        # start eval of sun state once initial list is filled
        if status_history.size() == status_history.maxsize():
            score = status_history.sum() / status_history.size()

            if score > PARAMS["vbdsd"]["measurement_threshold"]:
                with FileLock(CONFIG_LOCK_PATH):
                    with open(PARAMS_FILE_PATH, "w") as f:
                        PARAMS["pyra"]["automation_is_running"] = True
                        json.dump(PARAMS, f, indent=2)
            else:
                # sun status bad
                with FileLock(CONFIG_LOCK_PATH):
                    with open(PARAMS_FILE_PATH, "w") as f:
                        PARAMS["pyra"]["automation_is_running"] = False
                        json.dump(PARAMS, f, indent=2)

        # wait rest of loop time
        elapsed_time = time.time()
        while (elapsed_time - start_time) < PARAMS["vbdsd"]["interval_time"]:
            time.sleep(1)
            elapsed_time = time.time()
