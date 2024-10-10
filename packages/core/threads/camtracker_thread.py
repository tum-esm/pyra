import os
import threading
import time
from typing import Literal
import psutil
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils

logger = utils.Logger(origin="camtracker")


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
