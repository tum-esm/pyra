import cv2 as cv
import time
import datetime
import astropy.units as astropy_units
from packages.core.utils import (
    ConfigInterface,
    Astronomy,
)


def test_picture():
    _CONFIG = ConfigInterface().read()

    cam = cv.VideoCapture(_CONFIG["helios"]["camera_id"])  #

    cam.set(3, 1280)  # width
    cam.set(4, 720)  # height
    cam.set(15, -12)  # exposure
    cam.set(10, 64)  # brightness
    cam.set(11, 64)  # contrast
    cam.set(12, 0)  # saturation
    cam.set(14, 0)  # gain

    current_sun_angle = Astronomy.get_current_sun_elevation()
    diff = 0
    if current_sun_angle < 4 * astropy_units.deg:
        exp = -9 + diff
    elif current_sun_angle < 6 * astropy_units.deg:
        exp = -10 + diff
    elif current_sun_angle < 10 * astropy_units.deg:
        exp = -11 + diff
    else:
        exp = -12 + diff

    cam.set(15, exp)

    for i in range(5):
        ret, frame = cam.read()

        path = "C:\\pyra-4\\runtime-data\\helios\\test_{}.jpg".format(
            str(datetime.datetime.now().strftime("%H-%M-%S"))
        )

        cv.imwrite(path, frame)
        time.sleep(5)

    cam.release()
