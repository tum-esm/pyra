import os
import time
import jdcal
import datetime
from packages.core import types, utils, interfaces


logger = utils.Logger(origin="sun-tracking")


class SunTracking:
    """SunTracking manages the software CamTracker. CamTracker controls moveable mirrors attached
    to the FTIR spectrometer EM27. These mirrors are sync with the current sun position to ensure
    direct sun light to be directed into the instrument. SunTracking will initialize CamTracker
    according to the current value of StateInterface: measurements_should_be_running.

    These mirrors are initialized at startup of CamTracker if it is called with the additional
    parameter "-autostart". CamTracker can be gracefully shut down with creating a stop.txt file
    in its directory. CamTracker creates multiple logfiles at run time that give information on
    its current status of tracking the sun. Most importantly motor offsets tells the difference
    between current sun angle and calculated sun positions. It happens from time to time that
    SunTracker fails to track the sun and is unable to reinitialize the tracking. If a certain
    motor offset threshold is reached the only way to fix the offset is to restart CamTracker.

    """

    def __init__(self, initial_config: types.ConfigDict):
        self._CONFIG = initial_config
        self.last_start_time = time.time()
        if self._CONFIG["general"]["test_mode"]:
            return

    def run(self, new_config: types.ConfigDict) -> None:
        """Called in every cycle of the main loop.
        Redas StateInterface: measurements_should_be_running and starts and stops CamTracker
        tracking."""

        # update to latest config
        self._CONFIG = new_config

        # Skip rest of the function if test mode is active
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping SunTracking in test mode")
            return

        logger.info("Running SunTracking")

        # check for automation state flank changes
        measurements_should_be_running = interfaces.StateInterface.read()[
            "measurements_should_be_running"
        ]

        # main logic for active automation
        # start sun tracking if supposed to be running and not active
        if measurements_should_be_running and not self.ct_application_running():
            logger.info("Start CamTracker")
            self.start_sun_tracking_automation()
            self.last_start_time = time.time()
            return

        # stops sun tracking if supposed to be not running and active
        if not measurements_should_be_running and self.ct_application_running():
            logger.info("Stop CamTracker")
            self.stop_sun_tracking_automation()
            return

        # check motor offset, if over params.threshold prepare to
        # shutdown CamTracker. Will be restarted in next run() cycle.
        # is only considered if tracking is already up for at least 5 minutes.
        if (
            self.ct_application_running()
            and (time.time() - self.last_start_time) > 300
            and not self.validate_tracker_position()
        ):
            logger.info("CamTracker Motor Position is over threshold.")
            logger.info("Stop CamTracker. Preparing for reinitialization.")
            self.stop_sun_tracking_automation()

    def ct_application_running(self) -> bool:
        """Checks if CamTracker is already running by identifying the active window.

        False if Application is currently not running on OS
        True if Application is currently running on OS
        """

        ct_path = self._CONFIG["camtracker"]["executable_path"]
        process_name = os.path.basename(ct_path)

        return interfaces.OSInterface.get_process_status(process_name) in [
            "running",
            "start_pending",
            "continue_pending",
            "pause_pending",
            "paused",
        ]

    def start_sun_tracking_automation(self) -> None:
        """Uses os.startfile() to start up the CamTracker executable with additional parameter
        "-automation". The paramter - automation will instruct CamTracker to automatically move the
        mirrors to the expected sun position during startup.

        Removes stop.txt file in CamTracker directory if present. This file is the current way of
        gracefully shutting down CamTracker and move the mirrors back to parking position.
        """

        # delete stop.txt file in camtracker folder if present
        self.clean_stop_file()

        ct_path = self._CONFIG["camtracker"]["executable_path"]

        # works only > python3.10
        # without cwd CT will have trouble loading its internal database)
        try:
            os.startfile(  # type: ignore
                os.path.basename(ct_path),
                cwd=os.path.dirname(ct_path),
                arguments="-autostart",
                show_cmd=2,
            )
        except AttributeError:
            pass

    def stop_sun_tracking_automation(self) -> None:
        """Tells the CamTracker application to end program and move mirrors
        to parking position.

        CamTracker has an internal check for a stop.txt file in its directory.
        After detection it will move it's mirrors to parking position and end itself.
        """

        # create stop.txt file in camtracker folder
        camtracker_directory = os.path.dirname(self._CONFIG["camtracker"]["executable_path"])

        f = open(os.path.join(camtracker_directory, "stop.txt"), "w")
        f.close()

    def clean_stop_file(self) -> None:
        """This function removes the stop.txt file to allow CamTracker to restart."""

        camtracker_directory = os.path.dirname(self._CONFIG["camtracker"]["executable_path"])
        stop_file_path = os.path.join(camtracker_directory, "stop.txt")

        if os.path.exists(stop_file_path):
            os.remove(stop_file_path)

    def read_ct_log_learn_az_elev(self) -> tuple[float, float, float, float, float, float]:
        """Reads the CamTracker Logfile: LEARN_Az_Elev.dat.

        Returns a list of string parameter: [
            Julian Date,
            Tracker Elevation,
            Tracker Azimuth,
            Elev Offset from Astro,
            Az Offset from Astro,
            Ellipse distance/px
        ]

        Raises AssertionError if log file is invalid.
        """

        # read azimuth and elevation motor offsets from camtracker logfiles
        ct_logfile_path = self._CONFIG["camtracker"]["learn_az_elev_path"]
        assert os.path.isfile(ct_logfile_path), "camtracker logfile not found"

        with open(ct_logfile_path) as f:
            last_line = f.readlines()[-1]

        # last_line: [Julian Date, Tracker Elevation, Tracker Azimuth,
        # Elev Offset from Astro, Az Offset from Astro, Ellipse distance/px]
        str_values = last_line.replace(" ", "").replace("\n", "").split(",")

        try:
            assert len(str_values) == 6
            float_values = tuple([float(v) for v in str_values])
        except (AssertionError, ValueError):
            raise AssertionError(f'invalid last logfile line "{last_line}"')

        # convert julian day to greg calendar as tuple (Year, Month, Day)
        jddate = jdcal.jd2gcal(float(last_line[0]), 0)[:3]

        # assert that the log file is up-to-date
        now = datetime.datetime.now()
        assert jddate == (
            now.year,
            now.month,
            now.day,
        ), f'date in file is too old: "{last_line}"'

        return float_values  # type: ignore

    def validate_tracker_position(self) -> bool:
        """Reads motor offsets and compares it with defined threshold.
        The motor offset defines the difference between the current active and calculated sun
        angle.

        Returns
        True -> Offsets are within threshold
        False -> CamTracker lost sun position
        """

        # fails if file integrity is broken
        tracker_status = self.read_ct_log_learn_az_elev()

        elev_offset: float = tracker_status[3]
        az_offeset: float = tracker_status[4]
        threshold: float = self._CONFIG["camtracker"]["motor_offset_threshold"]

        return (abs(elev_offset) <= threshold) and (abs(az_offeset) <= threshold)

    def test_setup(self) -> None:
        """
        Function to test the functonality of this module. Starts up CamTracker to initialize the
        tracking mirrors. Then moves mirrors back to parking position and shuts dosn CamTracker.
        """
        if not self.ct_application_running():
            self.start_sun_tracking_automation()
            for _ in range(10):
                if self.ct_application_running():
                    break
                time.sleep(6)

        assert self.ct_application_running()
        self.stop_sun_tracking_automation()
        time.sleep(10)
        assert not self.ct_application_running()
