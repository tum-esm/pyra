# filename          : vbdsd.py
# description  : Vision-Based Direct Sunlight Detector
#==============================================================================
# author            : Benno Voggenreiter
# email             : -
# date              : 20190719
# version           : 1.0
# notes             : Created by Benno Voggenreiter (Master's Thesis)
# license           : -
# py version        : 2.7
#==============================================================================
# author            : Benno Voggenreiter
# email             : -
# date              : 20210226
# version           : 2.0
# notes             : Improved by Nikolas Hars (Bachelor's Thesis)
# license           : -
# py version        : 2.7
#==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220328
# version           : 3.0
# notes             : Upgrade to Python 3.10 and refactoring for Pyra 4.
# license           : -
# py version        : 3.10
#==============================================================================

import cv2 as cv
import time
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import sys
import logging
import smtplib
from UtilityModule import ReadWriteFiles
import glob
import imutils
import numpy as np


def init_cam(cam_id):

    cam = cv.VideoCapture(cam_id)
    cam.release()
    height = 720 # 768
    width = 1280 # 1024

    status = False
    for trial in range(1, 5):
        # print('Initializing Camera...Trial: {:.0f}'.format(trial))
        cam = cv.VideoCapture(cam_id)
        time.sleep(1)
        if cam.isOpened():
            cam.set(3, width)
            cam.set(4, height)
            cam.set(15, -12)    # exposure
            cam.set(10, 64)     # brightness
            cam.set(11, 64)     # contrast
            cam.set(12, 0)      # saturation
            cam.set(14, 0)      # gain
            status = True
            cam.read()
            break
    if status:
        return cam
    else:
        return None


def get_tracker_position():
    conf_file = ReadWriteFiles()
    height = float(conf_file.config_file['Camtracker Config File Height'])
    longitude = float(conf_file.config_file['Camtracker Config File Longitude'])
    latitude = float(conf_file.config_file['Camtracker Config File Latitude'])
    loc = coord.EarthLocation(lon=longitude * u.deg, lat=latitude * u.deg, height=height * u.km)
    return height, longitude, latitude, loc


def get_interval_time():
    conf_file = ReadWriteFiles()
    t_interval = conf_file.config_file['DSD Interval Time']
    return float(t_interval)


def get_period_time():
    conf_file = ReadWriteFiles()
    t_period = conf_file.config_file['DSD Period Time']
    return float(t_period)

def eval_sun_state_new(frame):
    """
    Sophisticated Contour Retrieval
    :param frame: Captured image from the sun detector camera
    :return: Status = -1, 0, 1.
            -1 --> Circle could not be detected --> Change Exposure and try again
             0 --> Circle detected but not enough contours on the projection plane
             1 --> Successfully detected contours
    """
    ret_val = -1

    x_pix, y_pix = 1280, 720
    blur = cv.medianBlur(frame, 15)
    frame_gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    img_b = cv.adaptiveThreshold(frame_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 21, 2)
    img_b = cv.medianBlur(img_b, 15)

    img_b, frame, border = extend_border(img_b, frame)

    contours, hierarchy = cv.findContours(img_b.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    # get Projection Plate Contour
    ppi_contour = None
    if len(contours) > 0:
        for i in range(len(contours)):
            if cv.contourArea(contours[i]) > 2000:
                x, y, w, h = cv.boundingRect(contours[i])
                if 300 < x < 1280 / 2 and 680 < float(h) < 740 and 0.8 < float(w) / float(h) < 1. / 0.8:
                    # Use constraints to find the projection plane
                    x_c, y_c, r = int(x + w / 2), int(y + h / 2), int((w + h) / 4)
                    logging.getLogger("VBDSD")
                    logging.info("radius %s" % r)
                    ppi_contour = contours[i]  # Save contour
                    break
                    # cv.drawContours(frame,contours[i], -1, (255,0,0),15)
        img_b = cv.bitwise_not(img_b)  # Black background
        if not ppi_contour is None:
            ret_val = 0


    if ret_val == 0:
        cv.drawContours(img_b, ppi_contour, -1, 0, 40)  # Draw over the white found contour: we might lose some contours
        # cv.drawContours(frame, ddi_contour, -1, (0,255,0), 20)
        # if they are connected to the border

        # Make borders black again
        cv.rectangle(img_b, (0, 0), (x_pix, border), (0), -1)
        cv.rectangle(img_b, (0, y_pix + border), (x_pix, y_pix + 2 * border), (0), -1)
        cv.circle(img_b, (x_c, y_c), r + 5, 255, 10)  # Draw white and black circle to seperate projection plate from outside
        cv.circle(img_b, (x_c, y_c), r - 2, 0, 5)

        contours_cropped, hierarchy = cv.findContours(img_b.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

        if len(contours_cropped) > 1:
            # Filter out small contours because they don't contain valuable information
            c_areas = []
            length_of_all_elements = 0
            for contour in contours_cropped:
                temp_area = cv.contourArea(contour)
                if temp_area >= 50:
                    length_of_all_elements += 1
                c_areas.append(temp_area)
            indices = np.argsort(c_areas)
            ppi = indices[-1]  # Outer contour of projection plate

            # Find the exact hierarchy to only check for contours that are children of the projection plane
            # Using a breadth-first search like approach
            all_elements = []
            structure = []
            level = 0
            Stay = True
            while Stay:
                this_level = []
                for i in indices:
                    if c_areas[i] < 50:
                        continue
                    put_in_level = False
                    if hierarchy[0][i][3] == -1 and level == 0:
                        put_in_level = True
                        for element in all_elements:
                            if i == element:
                                put_in_level = False
                                break
                        if put_in_level:
                            all_elements.append(i)
                            this_level.append(i)
                    elif level != 0:
                        for element in structure[level - 1]:
                            if hierarchy[0][i][3] == element:
                                put_in_level = True
                                for single_number in all_elements:
                                    if i == single_number:
                                        put_in_level = False
                                        break
                                if put_in_level:
                                    all_elements.append(i)
                                    this_level.append(i)
                if len(this_level) > 0:
                    level += 1
                    structure.append(this_level)
                if len(all_elements) == length_of_all_elements:
                    Stay = False
                    break

            # Check the size and parents and level of contour
            font = cv.FONT_HERSHEY_SIMPLEX
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (255, 255, 255)]
            areas = [0]
            for i in range(len(structure)):
                for element in structure[i]:
                    x, y, w, h = cv.boundingRect(contours_cropped[element])
                    pos = (x, y)
                    if hierarchy[0][element][3] == ppi + 1 or element == ppi or element == ppi + 1:
                        # if parent of current contour is inner circle: check area
                        # if contour = inner or outer pp (projection plate) --> draw as reference
                        if i > 1:
                            areas.append(c_areas[element])
                        if c_areas[element] > 2000 and i > 1:  # Hierarchy > 1 so is child of ppi and ppi+1
                            ret_val = 1
                            cv.drawContours(frame, contours_cropped[element], -1, colors[4], 4)
                            cv.putText(frame, ('%s (%s)' % (element, i)), pos, font, 1, colors[4], 2, 10)
                        else:
                            cv.drawContours(frame, contours_cropped[element], -1, colors[i], 4)
                            cv.putText(frame, ('%s (%s)' % (element, i)), pos, font, 1, colors[i], 2, 10)
                    else:
                        cv.drawContours(frame, contours_cropped[element], -1, colors[5], 4)
                        cv.putText(frame, ('%s (%s)' % (element, i)), pos, font, 1, colors[5], 2, 10)
            area = sum(areas)
            if len(areas) > 5:
                if np.mean(areas[1:]) > 500 or area > 2000:
                    ret_val = 1
    return ret_val, frame


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


def extend_border(img,frame):
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

def eval_sun_state_old(frame):

    blur = cv.medianBlur(frame, 15)
    frame_gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    img_b = cv.adaptiveThreshold(frame_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 17, 2)
    img_b = cv.medianBlur(img_b, 15)
    img_b = img_b[10:700, :]
    contours, hierarchy = cv.findContours(img_b, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    img_b = cv.medianBlur(img_b, 15)

    # get contours in binary frame
    if len(contours) <= 1:
     	#print('nosun')
      	return 0
    if len(contours) > 1:
        # get biggest contour which is projection plate
        # c = sorted(contours, key=cv.contourArea, reverse=True)
        # cv.drawContours(frame_gray, c[0], -1, 255, 1)
        # get pixel coordinates of bounding rectangle around projection plate
        x, y, w, h = cv.boundingRect(contours[(np.amax(hierarchy[0], axis=0)[0] - 1)])
        # cv.rectangle(img_b, (x, y), (x + w, y + h), 255, 1)
        # draw white circle on projection plate to separate
        # shadow contours from plate contours
        cv.circle(img_b, (x + w/2, y + h/2), h/2, 255, 3)
        # search for contours again
        contours_cropped, hierarchy = cv.findContours(img_b, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

        #for n in range(0, len(contours_cropped)):
        #    cv.drawContours(frame_gray, contours_cropped[n], -1, 255, 1)
        #    cv.imshow('contours_cropped', frame_gray)
        #    cv.waitKey()

        #print(hierarchy)
        if len(contours_cropped) != 0:
            for i in range(0, len(contours_cropped)):
                area = cv.contourArea(contours_cropped[i])
                #print(hierarchy[0][i])
                #print(area)
                if(hierarchy[0][i][3]) >= 0 and float(area) > 2000:
                    #print('sun')
                    return 1
	return 0


def get_image_storage_path():
    conf_file = ReadWriteFiles()
    path = conf_file.config_file['DSD Image Storage Path']
    return path


def get_angle_thres():
    conf_file = ReadWriteFiles()
    min_angle = conf_file.config_file['DSD Min Angle']
    return min_angle


def get_m_thres():
    conf_file = ReadWriteFiles()
    thr = conf_file.config_file['DSD Measurement Thres']
    return float(thr)


def get_a_thres():
    conf_file = ReadWriteFiles()
    thr = conf_file.config_file['DSD Automation Thres']
    return float(thr)


def get_cam_id():
    conf_file = ReadWriteFiles()
    cam_id = conf_file.config_file['DSD Cam ID']
    return int(cam_id)


def calc_sun_angle_deg(loc):
    now = Time.now()
    altaz = coord.AltAz(location=loc, obstime=now)
    sun = coord.get_sun(now)
    sun_angle_deg = sun.transform_to(altaz).alt
    return sun_angle_deg

def debug_log(file_name, msg):
    f = open(file_name, 'a')
    f.write(msg)
    f.close()

