# ==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220401
# version           : 3.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# CamTracker (ct) is a software that controls two electro motors that are
# connected to mirrors. It tracks the sun movement and allows the spectrometer
# to follow the sun in the course of the day.
# ==============================================================================

# TODO: Implement this for the "Camtracker" software
# Later, make an abstract base class that enforces a standard interface
# to be implemented for any software like "Camtracker"

import os
import jdcal
import datetime

# the following imports should be provided by pywin32
try:
    import win32con
    import win32ui
    import win32process

    windows_libraries_available = True
except ModuleNotFoundError:
    windows_libraries_available = False

from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.sun-tracking")


class SunTracking:
    def __init__(self):
        self._PARAMS = {}
        self._SETUP = {}
        if not windows_libraries_available:
            logger.info("Windows libraries not available, class is inactive")
            return

    def run(self, new_setup: dict, new_parameters: dict):
        self._SETUP, self._PARAMS = new_setup, new_parameters

        if not windows_libraries_available:
            return

        logger.info("Running SunTracking")

        # check for PYRA Test Mode status
        if self._PARAMS["pyra"]["test_mode"] == 1:
            logger.info("Test mode active.")
            return

        # automation is not active or was deactivated recently
        # TODO: Prüfen ob Flankenwechsel notwendig
        if self._PARAMS["pyra"]["automation_is_running"] == 0:

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
        # exe call with -automation
        # http://timgolden.me.uk/pywin32-docs/win32process.html
        camtracker_call = (
            self._SETUP["camtracker"]["executable_full_path"] + " -automation"
        )
        hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(
            None,
            camtracker_call,
            None,
            None,
            0,
            win32con.NORMAL_PRIORITY_CLASS,
            None,
            None,
            win32process.STARTUPINFO(),
        )

        return (hProcess, hThread, dwProcessId, dwThreadId)

    def __stop_sun_tracking_automation(self):
        """Tells the CamTracker application to end program and move mirrors
        to parking position.

        CamTracker has an internal check for a stop.txt file in its directory
        and will do a clean shutdown.
        """

        # create stop.txt file in camtracker folder
        camtracker_directory = os.path.dirname(
            self._SETUP["camtracker"]["executable_full_path"]
        )
        f = open(camtracker_directory + "stop.txt", "w")
        f.close()

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
        target = self._SETUP["camtracker"]["learn_az_elev_path"]

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
        target = self._SETUP["camtracker"]["sun_intensity_path"]

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
        threshold = self._PARAMS["camtracker"]["motor_offset_treshold"]

        if (elev_offset > threshold) or (az_offeset > threshold):
            return False

        return True