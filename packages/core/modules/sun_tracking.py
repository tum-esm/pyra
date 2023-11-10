from typing import Literal, Optional
import sys
import os
import time
import datetime
import psutil
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="sun-tracking")


class SunTracking:
    """SunTracking manages the software CamTracker. CamTracker controls
    moveable mirrors attached to the FTIR spectrometer EM27. These mirrors
    are sync with the current sun position to ensure direct sun light to
    be directed into the instrument. SunTracking will initialize CamTracker
    according to the current value of StateInterface:
    measurements_should_be_running.

    These mirrors are initialized at startup of CamTracker if it is called
    with the additional parameter `-autostart`. CamTracker can be gracefully
    shut down with creating a stop.txt file in its directory. CamTracker
    creates multiple logfiles at run time that give information on its
    current status of tracking the sun. Most importantly motor offsets tells
    the differencebetween current sun angle and calculated sun positions. It
    happens from time to time that SunTracker fails to track the sun and is
    unable to reinitialize the tracking. If a certain motor offset threshold
    is reached the only way to fix the offset is to restart CamTracker."""
    def __init__(self, initial_config: types.Config):
        self.config = initial_config
        self.last_start_time = time.time()
        self.waiting_for_shutdown: bool = False

    def run(self, new_config: types.Config) -> None:
        """Called in every cycle of the main loop. Start and stops CamTracker
        based on `StateInterface.measurements_should_be_running`."""

        # update to latest config
        self.config = new_config

        # Skip rest of the function if test mode is active
        if self.config.general.test_mode:
            logger.info("Skipping SunTracking in test mode")
            return
        else:
            logger.info("Running SunTracking")

        # check for automation state flank changes
        camtracker_is_running = self.camtracker_is_running()
        measurements_should_be_running = (
            interfaces.StateInterface.load_state().
            measurements_should_be_running
        ) or False

        # if CamTracker is supposed to shut down but is
        # still running wait until it has shut down
        if self.waiting_for_shutdown:
            if camtracker_is_running:
                logger.debug("Waiting for CamTracker to shut down")
                self.stop_sun_tracking_automation()
                return
            else:
                logger.info("CamTracker has shut down")
                self.waiting_for_shutdown = False

        # main logic for active automation
        # start sun tracking if supposed to be running and not active
        if measurements_should_be_running and (not camtracker_is_running):
            logger.info("Starting CamTracker")
            self.start_sun_tracking_automation()
            self.last_start_time = time.time()
            return

        # stops sun tracking if supposed to be not running and active
        if not measurements_should_be_running and camtracker_is_running:
            logger.info("Stopping CamTracker")
            self.stop_sun_tracking_automation()
            return

        # check motor offset, if over params.threshold prepare to
        # shutdown CamTracker. Will be restarted in next run() cycle.
        # is only considered if tracking is already up for at least 5 minutes.
        if not camtracker_is_running:
            logger.debug("CamTracker is not running")
            return

        if (time.time() - self.last_start_time) < 300:
            logger.debug(
                "Skipping CamTracker state validation when " +
                "it has been started less than 5 minutes ago"
            )
            return

        # check the current positions of the CamTracker motors
        # and the TUM PLC cover and restart CamTracker if they
        # are not in the expected position
        restart_camtracker: bool = False

        logger.debug("Checking CamTracker motor position")
        motor_position_state = self.check_camtracker_motor_position()

        if self.config.tum_plc is not None:
            logger.debug("Checking TUM enclosure cover position")
            cover_position_state = self.check_tum_plc_cover_position()
            if cover_position_state == "angle not reported":
                logger.debug("TUM enclosure cover position is unknown.")
            if cover_position_state == "invalid":
                logger.info("TUM enclosure cover is closed.")
                if self.config.camtracker.restart_if_cover_remains_closed:
                    restart_camtracker = True
            if cover_position_state == "valid":
                logger.debug("TUM enclosure cover is open.")

        if motor_position_state == "logs too old":
            logger.debug("CamTracker motor position is unknown (no log line).")
            if self.config.camtracker.restart_if_logs_are_too_old:
                restart_camtracker = True
        if motor_position_state == "invalid":
            logger.info("CamTracker motor position is over threshold.")
            restart_camtracker = True
        if motor_position_state == "valid":
            logger.debug("CamTracker motor position is valid.")

        if restart_camtracker:
            logger.info("Stopping CamTracker because it is in an invalid state")
            self.stop_sun_tracking_automation()

    def camtracker_is_running(self) -> bool:
        """Checks if CamTracker is already running by searching for processes with
        the executable `opus.exe` or `OpusCore.exe`

        Returns: `True` if Application is currently running and `False` if not."""

        for p in psutil.process_iter():
            name = p.name().lower()
            if name.startswith("camtracker") and name.endswith(".exe"):
                return True

        return False

    def start_sun_tracking_automation(self) -> None:
        """Uses os.startfile() to start up the CamTracker executable with
        additional parameter "-automation". The paramter - automation will
        instruct CamTracker to automatically move the mirrors to the expected
        sun position during startup.

        Removes stop.txt file in CamTracker directory if present. This file
        is the current way of gracefully shutting down CamTracker and move
        the mirrors back to parking position."""

        interfaces.ActivityHistoryInterface.add_datapoint(camtracker_startups=1)

        # delete stop.txt file in camtracker folder if present
        self.remove_stop_file()

        # works only >= python3.10
        # without cwd CT will have trouble loading its internal database)
        assert (sys.version_info.major == 3) and (
            sys.version_info.minor >= 10
        ), "This only works with Python 3.10 or higher"
        try:
            os.startfile(  # type: ignore
                os.path.basename(self.config.camtracker.executable_path.root),
                cwd=os.path.dirname(self.config.camtracker.executable_path.root),
                arguments="-autostart",
                show_cmd=2,
            )
        except AttributeError:
            pass

    @property
    def stop_file_path(self) -> str:
        """Returns the path to the stop.txt file in CamTracker directory."""

        return os.path.join(
            os.path.dirname(self.config.camtracker.executable_path.root),
            "stop.txt"
        )

    def stop_sun_tracking_automation(self) -> None:
        """Tells the CamTracker application to end program and move mirrors
        to parking position.

        CamTracker has an internal check for a stop.txt file in its directory.
        After detection it will move it's mirrors to parking position and end
        itself."""

        self.waiting_for_shutdown = True
        with open(self.stop_file_path) as f:
            f.write("")

    def remove_stop_file(self) -> None:
        """This function removes the stop.txt file to allow CamTracker to restart."""

        if os.path.exists(self.stop_file_path):
            os.remove(self.stop_file_path)

    def _read_ct_log_learn_az_elev(
        self,
    ) -> Optional[tuple[datetime.datetime, float, float, float, float, float]]:
        """Reads the CamTracker Logfile: LEARN_Az_Elev.dat.

        Returns:  A list of string parameters [datetime, Tracker Elevation,
                  Tracker Azimuth, Elev Offset from Astro, Az Offset from Astro,
                  Ellipse distance/px] or None if the last log line is older than
                  5 minutes.

        Raises:
            AssertionError: if last log line is in an invalid format
        """

        # read azimuth and elevation motor offsets from camtracker logfiles
        ct_logfile_path = self.config.camtracker.learn_az_elev_path.root
        assert os.path.isfile(ct_logfile_path), "camtracker logfile not found"

        last_line = utils.read_last_file_line(ct_logfile_path)

        # last_line: [Julian Date, Tracker Elevation, Tracker Azimuth,
        # Elev Offset from Astro, Az Offset from Astro, Ellipse distance/px]
        str_values = last_line.replace(" ", "").replace("\n", "").split(",")

        try:
            assert len(str_values) == 6
            float_values = (
                float(str_values[0]),
                float(str_values[1]),
                float(str_values[2]),
                float(str_values[3]),
                float(str_values[4]),
                float(str_values[5]),
            )
        except (AssertionError, ValueError):
            raise AssertionError(f'invalid last logfile line "{last_line}"')

        # convert julian day datetime
        logline_datetime = (
            datetime.datetime(1858, 11, 17) +
            datetime.timedelta(float_values[0] - 2400000.500)
        )

        logline_age_in_seconds = (datetime.datetime.now() -
                                  logline_datetime).total_seconds()

        # assert that the log file is up-to-date
        if logline_age_in_seconds > 300:
            logger.warning(
                f"Last line in CamTracker logfile is older " +
                f"than 5 minutes but from {logline_datetime}"
            )
            return None

        return (logline_datetime, *float_values[1 :])

    def check_camtracker_motor_position(
        self
    ) -> Literal["logs too old", "valid", "invalid"]:
        """Checks whether CamTracker is running and is pointing
        in the right direction.

        Reads in the `LEARN_Az_Elev.dat` logfile, if the last line is older
        than 5 minutes, the function returns "logs too old".

        If the last logline is younger than 5 minutes, the function returns
        "valid" if the motor offsets are within the defined threshold and
        "invalid" if the motor offsets are outside the threshold."""

        # fails if file integrity is broken
        tracker_status = self._read_ct_log_learn_az_elev()
        if tracker_status is None:
            return "logs too old"

        elev_offset: float = tracker_status[3]
        az_offeset: float = tracker_status[4]
        threshold: float = self.config.camtracker.motor_offset_threshold

        elev_offset_within_bounds = abs(elev_offset) <= threshold
        az_offeset_within_bounds = abs(az_offeset) <= threshold
        if elev_offset_within_bounds and az_offeset_within_bounds:
            return "valid"
        else:
            return "invalid"

    def check_tum_plc_cover_position(
        self
    ) -> Literal["angle not reported", "valid", "invalid"]:
        """Checks whether the TUM PLC cover is open or closed. Returns
        "angle not reported" if the cover position has not beenreported
        by the PLC yet."""

        current_cover_angle = interfaces.StateInterface.load_state(
        ).plc_state.actors.current_angle

        if current_cover_angle is None:
            return "angle not reported"
        if 20 < (abs(current_cover_angle) % 360) < 340:
            return "valid"
        else:
            return "invalid"

    def test_setup(self) -> None:
        """Function to test the functonality of this module. Starts up
        CamTracker to initialize the tracking mirrors. Then moves mirrors
        back to parking position and shuts dosn CamTracker."""
        if not self.camtracker_is_running():
            self.start_sun_tracking_automation()
            for _ in range(10):
                if self.camtracker_is_running():
                    break
                time.sleep(6)

        assert self.camtracker_is_running()
        self.stop_sun_tracking_automation()
        time.sleep(10)
        assert not self.camtracker_is_running()
