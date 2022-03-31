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
import logging
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

    # TODO: Ordnung in das Chaos bringen

    PARAMS, SETUP = read_json_files()
    #while(1)
    # if "vbdsd_automation_status" == 1 do...
    valid_angle_flag = False

    while not _stop.isSet():
        # calculate new sun angle
        sun_angle_deg = calc_sun_angle_deg(loc)

        # power spectrometer if sun angle bigger than 10 degrees
        # print('Sun Angle: {:.2f}'.format(self.sun_angle_deg))
        if not heating_flag:
            if sun_angle_deg >= 10 * astropy.units.deg:
                heating_flag = True


        # check whether angle is valid ( >15°)
        if sun_angle_deg > PARAMS["vbdsd_min_angle"]:
            logging.INFO("Minimum sun angle reached.")
            if not self.valid_angle_flag:
                valid_angle_flag = True

            n = PARAMS["vbdsd_interval_time"] / PARAMS["vbdsd_period_time"]

            logging.INFO("Capturing and Analysing {:.0f} Images in {:.2f} seconds ...".format(n, PARAMS["vbdsd_interval_time"]))

            image_path = image_storage_path + '//img_' + datetime.now().date().strftime('%Y_%m_%d') + '/'
            # make sure image path actually exists


            #for loop with n
                        status, frame = self.process_vbdsd_image()
                        if status == -1:
                            self.change_exposure(1)
                            status, frame = self.process_vbdsd_image()
                            if status == -1:
                                status = 0
                    except:  # join() causes an exception
                        status = 0
                        ui.write_to_log('WARNING', 'DSDthread', 'A frame could not be evaluated')
                        pass
                else:
                    break
                # store the images with CamTracker status for evaluation purpose
                self.dsd_logger.debug("get_ct_status")
                ct_status = ui.check_SunTracker_status_SunIntensity()
                if img_path_exists:
                    self.dsd_logger.debug("save_image")
                    cv.imwrite(self.image_path + '/' + datetime.now().time().strftime('%H_%M_%S_')
                               + ct_status + "_exp_" + str(self.exp) + '_' + str(status) + '.jpg', frame)

                self.results.append(status)
                if len(self.results) == self.n:
                    self.dsd_logger.debug("15 Images are captured")
                    break
                else:
                    self.change_exposure()
                    elapsed_time = time.time() - start_time
                    self.dsd_logger.debug("Elapsed Time = {}".format(int(elapsed_time)))
                    timeout = self.t_period - abs(elapsed_time)
                    self.dsd_logger.debug("Timeout = {}".format(int(timeout)))
                    if timeout <= 0:
                        timeout = 0.01
                    # print('VBDSD single image: %s s' % elapsed_time)
                    self.wait.acquire()
                    self.wait.wait(timeout=timeout)
                    self.dsd_logger.debug("self.wait.wait is timed out")

            elapsed_time0 = time.time() - start_time0
            # print('VBDSD all Images: %s s' % elapsed_time0)
            if self._stop.isSet() or len(self.results) != self.n:
                break

            self.score = float(sum(self.results)) / float(len(self.results))
            if self.score >= self.m_thres:
                self.status = 'GOOD'
            else:
                self.status = 'BAD'

            ui.write_to_log('INFO', 'DSDthread', 'VBDSD Results: ' + ', '
                            .join(['%.f' % (self.results[n]) for n in xrange(len(self.results))]))
            ui.write_to_log('INFO', 'DSDthread', 'Score: {:.2f}% ({:.0f}/{:.0f}) --> Sun Status: '
                            .format(self.score * 100.0, sum(self.results), len(self.results)) + self.status)
            self.results[:] = []
            # score > m_thres
            if not ui.indicatorRain.isChecked():
                if self.score >= self.m_thres:
                    self.dsd_logger.debug("Score > Measure")
                    if ui.resetButton.isEnabled():
                        ui.write_to_log('INFO', 'DSDthread', 'Resetting after rain')
                        ui.resetButton.click()
                        self.wait.acquire()
                        self.wait.wait(timeout=6.0)
                    if not ui.autoUpdateSwitch.isChecked() and not self._stop.isSet():
                        ui.write_to_log('INFO', 'DSDthread', 'Synchronise Cover')
                        ui.autoUpdateSwitch.setChecked(True)
                    # start CT and OPUS (start automation)
                    else:
                        self.dsd_logger.debug("autoUpdateSwitch is Checked or stop is set, so no: Synchronise Cover")
                    if ui.pushButton__start_automation.isEnabled() and not self._stop.isSet():
                        start_time1 = time.time()
                        ui.write_to_log('INFO', 'DSDthread', 'Automation START')
                        ui.pushButton__start_automation.click()
                        while not ui.pushButton_start_measurement.isEnabled() and not self._stop.isSet():
                            self.wait.acquire()
                            self.wait.wait(timeout=1.0)  # TODO: Infinite loop in Log_2020_11_16
                        # print('Start Automation Time: %s' % (time.time() - start_time1))
                    # start measurement
                    if ui.pushButton_start_measurement.isEnabled() and not self._stop.isSet():
                        start_time2 = time.time()
                        Vbdsd.debug_log(self.debug_file, 'Measurement START: \n'
                                        + datetime.now().strftime("%m/%d/%Y") + '\n'
                                        + datetime.now().time().strftime("%H:%M:%S") + '\n')
                        ui.write_to_log('INFO', 'DSDthread', 'Measurement START')
                        ui.pushButton_start_measurement.click()
                        while not ui.pushButton_stop_measurement.isEnabled() and not self._stop.isSet():
                            self.wait.acquire()
                            self.wait.wait(timeout=1.0)
                    else:
                        self.dsd_logger.debug("Start Measurement not enabled or stop is set")
                        # print('Start Measurement Time: %s' % (time.time() - start_time2))
                # stop measurement
                else:
                    self.dsd_logger.debug("Stop Measurement")
                    if ui.pushButton_stop_measurement.isEnabled() and not self._stop.isSet():
                        start_time3 = time.time()
                        ui.write_to_log('INFO', 'DSDthread', 'Measurement STOP: Inappropriate Sun Intensity')
                        Vbdsd.debug_log(self.debug_file, 'Measurement STOP: \n'
                                        + datetime.now().strftime("%m/%d/%Y") + '\n'
                                        + datetime.now().time().strftime("%H:%M:%S") + '\n')
                        ui.pushButton_stop_measurement.click()
                        while not ui.pushButton_start_measurement.isEnabled() and not self._stop.isSet():
                            self.dsd_logger.debug("Start Measurement not enabled - In Loop")
                            self.wait.acquire()
                            self.wait.wait(timeout=1.0)
                        # print('Stop Measurement Time: %s' % (time.time() - start_time3))
                    else:
                        self.dsd_logger.debug("Stop Measurement not enabled or stop is set")
                    # score < a_thres
                    if self.score < self.a_thres:
                        self.dsd_logger.debug("Score < Automation")
                        start_time4 = time.time()
                        if ui.pushButton__stop_automation.isEnabled() and not self._stop.isSet():
                            ui.write_to_log('INFO', 'DSDthread', 'Automation STOP: Inappropriate Sun Intensity')
                            ui.pushButton__stop_automation.click()
                            while not ui.pushButton__start_automation.isEnabled() and not self._stop.isSet():
                                self.dsd_logger.debug("Start Automation not enabled - In Loop")
                                self.wait.acquire()
                                self.wait.wait(timeout=1.0)
                            # print('Stop Automation Time: %s' % (time.time() - start_time4))
                        else:
                            self.dsd_logger.debug("Stop Automation not enabled or stop is set")
                elapsed_time = time.time() - start_time
                self.dsd_logger.debug("Elapsed Time = {}".format(int(elapsed_time)))
                timeout = self.t_period - abs(elapsed_time)
                self.dsd_logger.debug("Timeout = {}".format(int(timeout)))
                if timeout <= 0:
                    timeout = 0.01
                self.wait.acquire()
                self.wait.wait(timeout=timeout)
                self.dsd_logger.debug("self.wait.wait is timed out")
            else:
                ui.write_to_log('INFO', 'DSDthread', 'Rain Detected')
                if ui.autoUpdateSwitch.isChecked():
                    ui.write_to_log('INFO', 'DSDthread', 'ECON Cover: CLOSE')
                    ui.closeCoverButton.clicked.emit(True)
                if ui.pushButton_stop_measurement.isEnabled() and not self._stop.isSet():
                    Vbdsd.debug_log(self.debug_file, 'Measurement STOP: \n'
                                    + datetime.now().strftime("%m/%d/%Y") + '\n'
                                    + datetime.now().time().strftime("%H:%M:%S") + '\n')
                    ui.write_to_log('INFO', 'DSDthread', 'Measurement Stopped')
                    ui.pushButton_stop_measurement.click()
                    while not ui.pushButton_start_measurement.isEnabled():
                        self.wait.acquire()
                        self.wait.wait(timeout=1.0)
                if ui.pushButton__stop_automation.isEnabled() and not self._stop.isSet():
                    ui.write_to_log('INFO', 'DSDthread', 'Automation Stopped')
                    ui.pushButton__stop_automation.click()
                    while not ui.pushButton__start_automation.isEnabled():
                        self.wait.acquire()
                        self.wait.wait(timeout=1.0)
                elapsed_time = time.time() - start_time
                self.dsd_logger.debug("Elapsed Time = {}".format(int(elapsed_time)))
                timeout = self.t_period - abs(elapsed_time)
                self.dsd_logger.debug("Timeout = {}".format(int(timeout)))
                if timeout <= 0:
                    timeout = 0.01
                self.wait.acquire()
                self.wait.wait(timeout=timeout)
                self.dsd_logger.debug("self.wait.wait is timed out")
        # inappropriate sun angle
        else:
            if self.valid_angle_flag:
                ui.write_to_log('INFO', 'DSDthread', 'Inappropriate Sun Angle: {:.2f}'.format(self.sun_angle_deg))

            # Sun angle out of range: stop measurement, stop automation, close ECON
            if ui.pushButton_stop_measurement.isEnabled() and not self._stop.isSet():
                ui.write_to_log('INFO', 'DSDthread', 'Measurement STOP: Inappropriate Sun Angle')
                Vbdsd.debug_log(self.debug_file, 'Measurement STOP: \n'
                                + datetime.now().strftime("%m/%d/%Y") + '\n'
                                + datetime.now().time().strftime("%H:%M:%S") + '\n')
                ui.pushButton_stop_measurement.click()
                while not ui.pushButton_start_measurement.isEnabled() and not self._stop.isSet():
                    self.wait.acquire()
                    self.wait.wait(timeout=1.0)

            if ui.pushButton__stop_automation.isEnabled() and not self._stop.isSet():
                ui.write_to_log('INFO', 'DSDthread', 'Automation STOP: Inappropriate Sun Angle')
                ui.pushButton__stop_automation.click()
                while not ui.pushButton__start_automation.isEnabled() and not self._stop.isSet():
                    self.wait.acquire()
                    self.wait.wait(timeout=1.0)

            if ui.autoUpdateSwitch.isChecked() and not self._stop.isSet():
                ui.write_to_log('INFO', 'DSDthread', 'Closing Cover')
                ui.closeCoverButton.clicked.emit(True)

            if self.sun_angle_deg < 10.0 * u.deg and self.heating_flag:
                ui.Spec_power.setChecked(False)
                ui.write_to_log('INFO', 'DSDthread', 'Sun Angle: {:.2f}'.format(self.sun_angle_deg))
                ui.write_to_log('INFO', 'DSDthread', 'Power off EM27')
                self.heating_flag = False
            self.valid_angle_flag = False
            time.sleep(15)
    ui.write_to_log('INFO', 'DSDthread', 'DSDthread stopped')
    ui.automated_mode = False