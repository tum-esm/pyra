from typing import Literal
import datetime
import os
import threading
import time
import psutil
import pydantic
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils

logger = utils.Logger(origin="camtracker")


class TrackerPosition(pydantic.BaseModel):
    dt: datetime.datetime = pydantic.Field(..., description="Datetime of the tracker position")
    elevation: float = pydantic.Field(..., description="Tracker elevation")
    azimuth: float = pydantic.Field(..., description="Tracker azimuth")
    elevation_offset: float = pydantic.Field(
        ..., description="Deviation from theoretical sun elevation to tracker elevation"
    )
    azimuth_offset: float = pydantic.Field(
        ..., description="Deviation from theoretical sun azimuth to tracker azimuth"
    )
    ellipse_distance: float = pydantic.Field(..., description="Ellipse distance/px")


class CamTrackerProgram:
    @staticmethod
    def start(config: types.Config) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        interfaces.ActivityHistoryInterface.add_datapoint(camtracker_startups=1)

        # removing old stop file
        stop_file_path = os.path.join(
            os.path.dirname(config.camtracker.executable_path.root), "stop.txt"
        )
        if os.path.exists(stop_file_path):
            os.remove(stop_file_path)

        logger.info("Starting CamTracker")
        os.startfile(  # type: ignore
            os.path.basename(config.camtracker.executable_path.root),
            cwd=os.path.dirname(config.camtracker.executable_path.root),
            arguments="-autostart",
            show_cmd=2,
        )
        tum_esm_utils.timing.wait_for_condition(
            is_successful=CamTrackerProgram.is_running,
            timeout_message="CamTracker did not start within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=8,
        )
        logger.info("Successfully started CamTracker")

    @staticmethod
    def is_running() -> bool:
        """Checks if CamTracker is already running by searching for processes with
        the executable `camtracker*.exe`."""

        logger.debug("Checking if CamTracker is running")
        for p in psutil.process_iter():
            try:
                name = p.name().lower()
                if name.startswith("camtracker") and name.endswith(".exe"):
                    return True
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass

        return False

    @staticmethod
    def stop(config: types.Config) -> None:
        """Closes OPUS via DDE/force kills it via psutil. If no DDEConnection
        is provided, the function will force kill OPUS right away."""

        stop_file_path = os.path.join(
            os.path.dirname(config.camtracker.executable_path.root), "stop.txt"
        )
        logger.info("Trying to stop CamTracker gracefully")
        with open(stop_file_path, "w") as f:
            f.write("")

        try:
            tum_esm_utils.timing.wait_for_condition(
                is_successful=lambda: not CamTrackerProgram.is_running(),
                timeout_seconds=90,
                check_interval_seconds=9,
            )
            logger.info("Successfully stopped CamTracker")
            return
        except TimeoutError as e:
            logger.error("Camtracker did not stop within 90 seconds.")

        logger.info("Force killing CamTracker")
        for p in psutil.process_iter():
            try:
                name = p.name().lower()
                if name.startswith("camtracker") and name.endswith(".exe"):
                    p.kill()
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass
        logger.info("Successfully force killed CamTracker")

    @staticmethod
    def read_tracker_position(config: types.Config) -> TrackerPosition:
        """Reads the CamTracker Logfile: LEARN_Az_Elev.dat.

        Returns:  Last logged tracker position

        Raises:
            AssertionError: if last log line is in an invalid format
        """

        # read azimuth and elevation motor offsets from camtracker logfiles
        ct_logfile_path = config.camtracker.learn_az_elev_path.root
        assert os.path.isfile(ct_logfile_path), "CamTracker logfile not found"

        try:
            last_line = utils.read_last_file_line(ct_logfile_path)
        except OSError as e:
            raise AssertionError(f"CamTracker logfile is empty: {e}")

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
            raise AssertionError(f'Invalid last logfile line "{last_line}"')

        return TrackerPosition(
            dt=(
                datetime.datetime(1858, 11, 17) + datetime.timedelta(float_values[0] - 2400000.500)
            ),
            elevation=float_values[1],
            azimuth=float_values[2],
            elev_offset=float_values[3],
            az_offset=float_values[4],
            ellipse_distance=float_values[5],
        )


class CamTrackerThread(AbstractThread):
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=CamTrackerThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        pass

    @staticmethod
    def check_tracker_motor_positions(
        config: types.Config
    ) -> Literal["no logs", "logs too old", "valid", "invalid"]:
        """Checks whether CamTracker is running and is pointing in the right direction.

        If the last logline is younger than 5 minutes, the function returns
        "valid" if the motor offsets are within the defined threshold and
        "invalid" if the motor offsets are outside the threshold."""

        try:
            tracker_position = CamTrackerProgram.read_tracker_position(config)
        except AssertionError as e:
            logger.error(f"Could not read tracker position: {e}")
            return "no logs"

        if tracker_position.dt < datetime.datetime.now() - datetime.timedelta(minutes=5):
            return "logs too old"

        if ((abs(tracker_position.azimuth_offset) <= config.camtracker.motor_offset_threshold) and
            (abs(tracker_position.elevation_offset) <= config.camtracker.motor_offset_threshold)):
            return "valid"
        else:
            return "invalid"

    @staticmethod
    def get_enclosure_cover_state(
        config: types.Config
    ) -> Literal["not configured", "angle not reported", "open", "closed"]:
        """Checks whether the TUM PLC cover is open or closed. Returns
        "angle not reported" if the cover position has not beenreported
        by the PLC yet."""

        if config.tum_plc is None:
            return "not configured"

        current_cover_angle = interfaces.StateInterface.load_state().plc_state.actors.current_angle

        if current_cover_angle is None:
            return "angle not reported"
        if 20 < ((current_cover_angle + 360) % 360) < 340:
            return "open"
        else:
            return "closed"

    @staticmethod
    def test_setup(self) -> None:
        """Function to test the functonality of this module. Starts up
        CamTracker to initialize the tracking mirrors. Then moves mirrors
        back to parking position and shuts dosn CamTracker."""

        assert (
            not CamTrackerProgram.is_running(),
            "This test cannot be run if CamTracker is already running"
        )
        config = types.Config.load()
        CamTrackerProgram.start(config)
        time.sleep(2)
        CamTrackerProgram.stop(config)
