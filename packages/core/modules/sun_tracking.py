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


# these imports are provided by pywin32
if sys.platform == "win32":
    import win32ui  # type: ignore


logger = Logger(origin="pyra.core.sun-tracking")


class SunTracking:
    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config
        if self._CONFIG["general"]["test_mode"]:
            return

    def run(self, new_config: dict):
        self._CONFIG = new_config
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping SunTracking in test mode")
            return

        logger.info("Running SunTracking")

        # automation is not active or was deactivated recently
        # TODO: Prüfen ob Flankenwechsel notwendig
        if not StateInterface.read()["vbdsd_indicates_good_conditions"]:
            if self.ct_application_running():
                logger.info("Stop CamTracker.")
                self.stop_sun_tracking_automation()
            return

        # main logic for active automation

        # start ct if not currently running
        if not self.ct_application_running():
            logger.info("Start CamTracker.")
            self.start_sun_tracking_automation()
            #give camtracker one loop time to move to position
            return


        # check motor offset, if over params.threshold prepare to
        # shutdown CamTracker. Will be restarted in next run() cycle.
        if not self.valdiate_tracker_position():
            logger.info("Stop CamTracker. Preparing for reinitialization.")
            self.stop_sun_tracking_automation()


    def ct_application_running(self):
        """Checks if CamTracker is already running by identifying the window.

        False if Application is currently not running on OS
        True if Application is currently running on OS
        """
        # FindWindow(className, windowName)
        # className: String, The window class name to find, else None
        # windowName: String, The window name (ie,title) to find, else None
        try:
            #TODO: remove hardcoding of name
            if win32ui.FindWindow(None, "CamTracker 3.9"):
                return True
        except win32ui.error:
            return False

    def start_sun_tracking_automation(self):
        """Uses os.startfile() to start up the CamTracker
        executable with additional parameter -automation.
        The paramter - automation will instruct CamTracker to automatically
        move the mirrors to the expected sun position during startup.
        """
        # delete stop.txt file in camtracker folder if present
        self.clean_stop_file()

        ct_path = self._CONFIG["camtracker"]["executable_path"]

        # works only > python3.10
        # without cwd CT will have trouble loading its internal database)
        os.startfile(
            os.path.basename(ct_path),
            cwd=os.path.dirname(ct_path),
            arguments="-autostart",
            show_cmd=2,
        )

    def stop_sun_tracking_automation(self):
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

    def read_ct_log_learn_az_elev(self):
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


    def valdiate_tracker_position(self):
        """Reads motor offsets and compares it with defined threshold.

        Returns
        True -> Offsets are within threshold
        False -> CamTracker lost sun position
        """

        tracker_status = self.read_ct_log_learn_az_elev()

        if None in tracker_status:
            return


        elev_offset = float(tracker_status[3])
        az_offeset = float(tracker_status[4])
        threshold = float(self._CONFIG["camtracker"]["motor_offset_threshold"])

        if (elev_offset > threshold) or (az_offeset > threshold):
            return False

        return True

    def test_setup(self):
        if sys.platform != "win32":
            return

        ct_is_running = self.ct_application_running
        if not ct_is_running:
            self.start_sun_tracking_automation()
            try_count = 0
            while try_count < 10:
                if self.ct_application_running:
                    break
                try_count += 1
                time.sleep(6)

        assert self.ct_application_running

        # time.sleep(20)

        self.stop_sun_tracking_automation()
        time.sleep(10)

        assert not self.ct_application_running

        assert False
