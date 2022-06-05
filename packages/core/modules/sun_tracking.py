# ==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220421
# version           : 1.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# CamTracker (ct) is a software that controls two electro motors that are
# connected to mirrors. It tracks the sun movement and allows the spectrometer
# to follow the sun in the course of the day.
# ==============================================================================

# This is an Implementation this for the "Camtracker" software
# Later, we will make an abstract base class that enforces a standard
# interface to be implemented for any software like "Camtracker"

import os
import sys
import time
import jdcal
import datetime
from packages.core.utils import StateInterface, Logger

# the following imports should be provided by pywin32
if sys.platform == "win32":
    import win32con
    import win32ui
    import win32process

logger = Logger(origin="pyra.core.sun-tracking")


class SunTracking:
    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config
        if sys.platform != "win32":
            print("The SunTracking class can only be tested on windows")
            return

    def run(self, new_config: dict):
        self._CONFIG = new_config

        if sys.platform != "win32":
            return

        logger.info("Running SunTracking")

        # check for PYRA Test Mode status
        if self._CONFIG["general"]["test_mode"] == 1:
            logger.info("Test mode active.")
            return

        # automation is not active or was deactivated recently
        # TODO: Prüfen ob Flankenwechsel notwendig
        if not StateInterface.read()["vbdsd_evaluation_is_positive"]:
            if self.__ct_application_running:
                self.__stop_sun_tracking_automation()
                logger.info("Stop CamTracker.")
            return

        # main logic for active automation

        # start ct if not currently running
        if not self.__ct_application_running:
            self.__start_sun_tracking_automation()
            logger.info("Start CamTracker.")

        # check motor offset, if over params.threshold prepare to
        # shutdown CamTracker. Will be restarted in next run() cycle.
        if not self.__valdiate_tracker_position:
            self.__stop_sun_tracking_automation()
            logger.info("Stop CamTracker. Preparing for reinitialization.")

    @property
    def __ct_application_running(self):
        """Checks if CamTracker is already running by identifying the window.

        False if Application is currently not running on OS
        True if Application is currently running on OS
        """
        # FindWindow(className, windowName)
        # className: String, The window class name to find, else None
        # windowName: String, The window name (ie,title) to find, else None
        try:
            if win32ui.FindWindow(None, "CamTracker 3.9"):
                return True
        except win32ui.error:
            return False

    def __start_sun_tracking_automation(self):
        """Uses win32process frm pywin32 module to start up the CamTracker
         executable with additional parameter -automation.
        The paramter - automation will instruct CamTracker to automatically
        move the mirrors to the expected sun position during startup.

         Returns pywin32 process information for later usage.
        """
        # delete stop.txt file in camtracker folder if present
        self.clean_stop_file()

        ct_path = self._CONFIG["camtracker"]["executable_path"]

        # works only > python3.10
        # without cwd CT will have trouble loading its internal database)
        os.startfile(
            path=os.path.filename(ct_path),
            cwd=os.path.basename(ct_path),
            arguments="-autostart",
            show_cmd=2,
        )

    def __stop_sun_tracking_automation(self):
        """Tells the CamTracker application to end program and move mirrors
        to parking position.

        CamTracker has an internal check for a stop.txt file in its directory
        and will do a clean shutdown.
        """

        # create stop.txt file in camtracker folder
        camtracker_directory = os.path.dirname(
            self._CONFIG["camtracker"]["executable_path"]
        )

        f = open(os.path.join(camtracker_directory, "stop.txt"), "w")
        f.close()

    def clean_stop_file(self):
        """CamTracker needs a stop.txt file to safely shutdown.
        This file needs to be removed after CamTracker shutdown.
        """

        camtracker_directory = os.path.dirname(
            self._CONFIG["camtracker"]["executable_path"]
        )
        stop_file_path = os.path.join(camtracker_directory, "stop.txt")

        if os.path.exists(stop_file_path):
            os.remove(stop_file_path)

    def __read_ct_log_learn_az_elev(self):
        """Reads the CamTracker Logfile: LEARN_Az_Elev.dat.

        Returns a list of string parameter:
        [
        Julian Date,
        Tracker Elevation,
        Tracker Azimuth,
        Elev Offset from Astro,
        Az Offset from Astro,
        Ellipse distance/px
        ]
        """
        # read azimuth and elevation motor offsets from camtracker logfiles
        target = self._CONFIG["camtracker"]["learn_az_elev_path"]

        if not os.path.isfile(target):
            return [None, None, None, None, None, None]

        f = open(target, "r")
        last_line = f.readlines()[-1]
        f.close()

        # last_line: [Julian Date, Tracker Elevation, Tracker Azimuth,
        # Elev Offset from Astro, Az Offset from Astro, Ellipse distance/px]
        last_line = last_line.replace(" ", "").replace("\n", "").split(",")

        # convert julian day to greg calendar as tuple (Year, Month, Day)
        jddate = jdcal.jd2gcal(float(last_line[0]), 0)[:3]

        # get current date(example below)
        # date = (Year, Month, Day)
        now = datetime.datetime.now()
        date = (now.year, now.month, now.day)

        # if the in the log file read date is up-to-date
        if date == jddate:
            return last_line
        else:
            return [None, None, None, None, None, None]

    def __read_ct_log_sunintensity(self):
        """Reads the CamTracker Logile: SunIntensity.dat.

        Returns the sun intensity as either 'good', 'bad', 'None'.
        """
        # check sun status logged by camtracker
        target = self._CONFIG["camtracker"]["sun_intensity_path"]

        if not os.path.isfile(target):
            return

        f = open(target, "r")
        last_line = f.readlines()[-1]
        f.close()

        sun_intensity = last_line.split(",")[3].replace(" ", "").replace("\n", "")

        # convert julian day to greg calendar as tuple (Year, Month, Day)
        jddate = jdcal.jd2gcal(
            float(last_line.replace(" ", "").replace("\n", "").split(",")[0]), 0
        )[:3]

        # get current date(example below)
        # date = (Year, Month, Day)
        now = datetime.datetime.now()
        date = (now.year, now.month, now.day)

        # if file is up to date
        if date == jddate:
            # returns either 'good' or 'bad'
            return sun_intensity

    @property
    def __valdiate_tracker_position(self):
        """Reads motor offsets and compares it with defined threshold.

        Returns
        True -> Offsets are within threshold
        False -> CamTracker lost sun position
        """

        tracker_status = self.__read_ct_log_learn_az_elev()

        if None in tracker_status:
            return

        elev_offset = tracker_status[3]
        az_offeset = tracker_status[4]
        threshold = self._CONFIG["camtracker"]["motor_offset_threshold"]

        if (elev_offset > threshold) or (az_offeset > threshold):
            return False

        return True

    def test_setup(self):
        if sys.platform != "win32":
            return

        ct_is_running = self.__ct_application_running
        if not ct_is_running:
            self.__start_sun_tracking_automation()
            try_count = 0
            while try_count < 10:
                if self.__ct_application_running:
                    break
                try_count += 1
                time.sleep(6)

        assert self.__ct_application_running

        # time.sleep(20)

        self.__stop_sun_tracking_automation()
        time.sleep(10)

        assert not self.__ct_application_running

        assert False
