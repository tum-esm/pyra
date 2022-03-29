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

import os
import time
import astropy
import cv2 as cv
import numpy as np
import json
from packages.core.validation import Validation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"

def read_json_files():
    """Reads and validates the available json config files.

    Returns
    SETUP:dict and PARAMS:dict as Tuple
    """
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

    status = False

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
            status = True
            cam.read()
            break
    if status:
        return cam
    else:
        return None

def eval_sun_state(frame):
    """
    Hough Detection ALgorithm
    """
    blur = cv.medianBlur(frame, 15)
    frame_gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    if frame_gray.shape[1] == 1280:  # Crop on sides
        frame_gray = frame_gray[:, 170:1100]
        frame = frame[:, 170:1100]

    img_b = cv.adaptiveThreshold(frame_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 23, 2)
    img_b = cv.medianBlur(img_b, 9)

    img_b, frame, border = extend_border(img_b, frame)

    circles = cv.HoughCircles(img_b, cv.HOUGH_GRADIENT, 1, 900,
                              param1=200, param2=1, minRadius=345, maxRadius=355)
    # (min + max) radius have to be quite exact.
    # 900 = Distance to next circle to prevent wrong circles

    if not circles is None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            cv.circle(img_b, center, radius - 10, 255, 30)
            cv.circle(img_b, center, radius - 20, 0, 15)

            cv.circle(frame, center, radius, 255, 5)

    else:
        return -1, frame

    contours, hierarchy = cv.findContours(img_b.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

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
                cv.putText(frame, ('%s' % (i)), pos, font, 1, color, 2, 10)
                areas.append(c_areas[i])
    cv.putText(frame, "%05d" % (np.sum(areas)), (10, y_length - 20), font, 1, (255, 255, 255), 2, 10)
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

def get_tracker_position():
    """get_tracker_position(): Reads out the height, the longitude and the
    latitude of the system from CamTrackerConfig.txt, and computes the location
    on earth. Therefore, the python package astropy [23] is imported, and its
    function coord.EarthLocation() is used. The read out parameters, as well as
    the computed location will be returned.
    """
    conf_file = ReadWriteFiles()
    height = float(conf_file.config_file['Camtracker Config File Height'])
    longitude = float(conf_file.config_file['Camtracker Config File Longitude'])
    latitude = float(conf_file.config_file['Camtracker Config File Latitude'])

    loc = astropy.coordinates.EarthLocation(lon=longitude * astropy.units.deg,
                                            lat=latitude * astropy.units.deg,
                                            height=height * astropy.units.km)
    return height, longitude, latitude, loc

def get_interval_time():
    """get_interval_time(): ReadsoutthetimeintervalDSDIntervalTimefromparameters.json,
    within images shall be captured and evaluated. During this interval, images
    will be captured and ana- lyzed after every user defined period.
    """
    conf_file = ReadWriteFiles()
    t_interval = conf_file.config_file['DSD Interval Time']
    return float(t_interval)

def get_period_time():
    """get_period_time(): Reads out the time period DSDP eriodT ime from
    parameters.json. Images will be captured and evaluated after every period for
     the user defined time interval.
     """
    conf_file = ReadWriteFiles()
    t_period = conf_file.config_file['DSD Period Time']
    return float(t_period)

def extend_border(img, frame):
    bordersize = 50  # Extend borders
    img_b = cv.copyMakeBorder(
        img,
        top=bordersize,
        bottom=bordersize,
        left=0,
        right=0,
        borderType=cv.BORDER_CONSTANT,
        value=[0, 0, 0]
    )

    frame = cv.copyMakeBorder(
        frame,
        top=bordersize,
        bottom=bordersize,
        left=0,
        right=0,
        borderType=cv.BORDER_CONSTANT,
        value=[0, 0, 0]
    )
    return img_b, frame, bordersize

def get_image_storage_path():
    """get_image_storage_path(): Reads out the path DSDImageStoragePath, where
    images cap- tured by the sensor shall be stored from parameters.json, and
    returns it as a string. The parameter therefore is.
    """
    conf_file = ReadWriteFiles()
    path = conf_file.config_file['DSD Image Storage Path']
    return path

def get_angle_thres():
    """get_angle_thres(): Reads out the minimum sun angle DSDMinAngle from
    parameters.json, at which the Bruker EM27/SUN is able to measure."""
    conf_file = ReadWriteFiles()
    min_angle = conf_file.config_file['DSD Min Angle']
    return min_angle

def get_m_thres():
    """get_m_thres(): Reads out the measurement threshold value DSDMeasurementThres
    for the evaluated images from parameters.json. If the percentage of images,
    captured during above men- tioned time interval and shadow was successfully
    detected within, exceeds this threshold, the measurement procedure will be
    initiated. Otherwise, a possible running measurement will be stopped.
    """
    conf_file = ReadWriteFiles()
    thr = conf_file.config_file['DSD Measurement Thres']
    return float(thr)

def get_a_thres():
    """get_a_thres(): Reads out the automation threshold value DSDAutomationT
    hres for the eval- uated images from parameters.json. If the percentage of
    images, captured during above mentioned time interval and shadow was
    successfully detected within, is below that threshold, OPUS and CamTracker
    will be terminated.
    """
    conf_file = ReadWriteFiles()
    thr = conf_file.config_file['DSD Automation Thres']
    return float(thr)

def get_cam_id():
    """get_cam_id(): Reads out the camera ID DSDCamID to connect with from
    parameters.json.
    """
    conf_file = ReadWriteFiles()
    cam_id = conf_file.config_file['DSD Cam ID']
    return int(cam_id)

if __name__ == "__main__":
    #while(1)
    # if "vbdsd_automation_status" == 1 do...
    pass