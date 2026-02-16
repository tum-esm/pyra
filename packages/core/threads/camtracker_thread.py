import datetime
import os
import threading
import time
from typing import Literal, Optional

import psutil
import pydantic
import tum_esm_utils

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


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
    def start(
        config: types.Config,
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        with interfaces.StateInterface.update_state(state_lock, logger) as s:
            s.activity.camtracker_startups += 1

        logger.info("Removing old stop.txt file")
        # this has to be done for two directories because new CamTracker versions
        # might look for this "stop.txt" file in the working directory instead of
        # the directory where the executable is located
        for d in [
            os.path.dirname(config.camtracker.executable_path.root),
            config.camtracker.working_directory_path.root,
        ]:
            stop_file_path = os.path.join(d, "stop.txt")
            if os.path.exists(stop_file_path):
                os.remove(stop_file_path)

        logger.info("Starting CamTracker")
        os.startfile(  # type: ignore
            config.camtracker.executable_path.root,
            cwd=config.camtracker.working_directory_path.root,
            arguments="-autostart",
            show_cmd=2,
        )
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: CamTrackerProgram.is_running(),
            timeout_message="CamTracker did not start within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=8,
        )
        logger.info(f"Successfully started CamTracker withing {dt:.2f} seconds")

    @staticmethod
    def is_running() -> bool:
        """Checks if CamTracker is already running by searching for processes with
        the executable `camtracker*.exe`."""

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
    def stop(config: types.Config, logger: utils.Logger) -> None:
        """Closes OPUS via DDE/force kills it via psutil. If no DDEConnection
        is provided, the function will force kill OPUS right away."""

        logger.info("Trying to stop CamTracker gracefully")
        # this has to be done for two directories because new CamTracker versions
        # might look for this "stop.txt" file in the working directory instead of
        # the directory where the executable is located
        for d in [
            os.path.dirname(config.camtracker.executable_path.root),
            config.camtracker.working_directory_path.root,
        ]:
            tum_esm_utils.files.dump_file(os.path.join(d, "stop.txt"), "")

        try:
            dt = tum_esm_utils.timing.wait_for_condition(
                is_successful=lambda: not CamTrackerProgram.is_running(),
                timeout_message="CamTracker did not stop within 90 seconds.",
                timeout_seconds=90,
                check_interval_seconds=9,
            )
            logger.info(f"Successfully stopped CamTracker gracefully within {dt:.2f} seconds")
            return
        except TimeoutError as e:
            logger.error(f"Could not stop CamTracker gracefully: {e}")

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
            raise AssertionError(f"CamTracker logfile is empty") from e

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
        except (AssertionError, ValueError) as e:
            raise AssertionError(f'Invalid last logfile line "{last_line}"') from e

        return TrackerPosition(
            dt=(
                datetime.datetime(1858, 11, 17) + datetime.timedelta(float_values[0] - 2400000.500)
            ),
            elevation=float_values[1],
            azimuth=float_values[2],
            elevation_offset=float_values[3],
            azimuth_offset=float_values[4],
            ellipse_distance=float_values[5],
        )


class CamTrackerThread(AbstractThread):
    logger_origin = "camtracker-thread"

    @staticmethod
    def should_be_running(
        config: types.Config,
        logger: utils.Logger,
    ) -> bool:
        """Based on the config, should the thread be running or not?"""

        return not config.general.test_mode

    @staticmethod
    def get_new_thread_object(
        logs_lock: threading.Lock,
    ) -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(
            target=CamTrackerThread.main,
            daemon=True,
            args=(logs_lock,),
        )

    @staticmethod
    def main(
        logs_lock: threading.Lock,
        headless: bool = False,
    ) -> None:
        """Main entrypoint of the thread."""

        logger = utils.Logger(origin="camtracker", lock=logs_lock, just_print=headless)
        logger.info("Starting CamTracker thread")
        last_camtracker_start_time: Optional[float] = None
        thread_start_time = time.time()

        state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
            filepath=interfaces.state_interface.STATE_LOCK_PATH,
            timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
            poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
        )

        # STOP CAMTRACKER IF IT IS RUNNING
        config = types.Config.load()

        while True:
            try:
                t1 = time.time()
                logger.debug("Starting iteration")

                if (t1 - thread_start_time) > 43200:
                    # Windows happens to have a problem with long-running multiprocesses/multithreads
                    logger.debug(
                        "Stopping and restarting thread after 12 hours for stability reasons"
                    )
                    return

                logger.debug("Loading configuration file")
                config = types.Config.load()

                camtracker_is_running = CamTrackerProgram.is_running()
                state = interfaces.StateInterface.load_state(state_lock, logger)
                measurements_should_be_running = bool(state.measurements_should_be_running)

                if config.general.test_mode:
                    logger.info("CamTracker thread is skipped in test mode")
                    time.sleep(15)
                    continue

                # RESOLVE COVER CLOSED WARNING WHEN IT IS RAINING

                if (state.last_bad_weather_detection is not None) and (
                    (time.time() - state.last_bad_weather_detection) < 180
                ):
                    if state.exceptions_state.has_subject(
                        "Camtracker was started but cover is closed."
                    ):
                        with interfaces.StateInterface.update_state(state_lock, logger) as s:
                            s.exceptions_state.clear_exception_subject(
                                subject="Camtracker was started but cover is closed."
                            )

                # START/STOP CAMTRACKER IF NECESSARY

                if measurements_should_be_running and (not camtracker_is_running):
                    logger.info("CamTracker should be running, but is not. Starting CamTracker.")
                    CamTrackerProgram.start(config, state_lock, logger)
                    last_camtracker_start_time = time.time()

                if (not measurements_should_be_running) and camtracker_is_running:
                    logger.info("CamTracker should not be running, but is. Stopping CamTracker.")
                    CamTrackerProgram.stop(config, logger)
                    camtracker_is_running = False
                    last_camtracker_start_time = None

                # CHECK WHETHER CAMTRACKER IS RUNNING CORRECTLY

                if measurements_should_be_running and (last_camtracker_start_time is not None):
                    if (time.time() - last_camtracker_start_time) < 180:
                        logger.info(
                            "Waiting 3 minutes after CamTracker start to check motor positions."
                        )
                    else:
                        logger.debug("Checking motor positions.")
                        result = CamTrackerThread.check_tracker_motor_positions(config, logger)
                        logger.debug(f"Tracker position check result: {result}")
                        match result:
                            case "no logs" | "logs too old":
                                if config.camtracker.restart_if_logs_are_too_old:
                                    logger.info("Restarting CamTracker because logs are too old.")
                                    CamTrackerProgram.stop(config, logger)
                                    continue
                            case "offsets too high":
                                logger.error(
                                    "Restarting CamTracker because tracker offsets are too high."
                                )
                                CamTrackerProgram.stop(config, logger)
                                continue
                            case "offsets are zero":
                                logger.warning(
                                    "CamTracker motor offsets are zero, waiting 30 seconds to confirm this state."
                                )
                                time.sleep(30)
                                result_after_waiting = (
                                    CamTrackerThread.check_tracker_motor_positions(config, logger)
                                )
                                if result_after_waiting == "offsets are zero":
                                    logger.error(
                                        "Restarting CamTracker because tracker offsets are zero for at least 30 seconds."
                                    )
                                    CamTrackerProgram.stop(config, logger)
                                    continue
                                else:
                                    # if the error is something else now, it will be handled in the next iteration
                                    logger.debug(
                                        "Tracker offsets are no longer zero after waiting 30 seconds."
                                    )
                            case "valid":
                                logger.debug("Tracker offsets are within threshold.")

                        logger.debug("Checking enclosure cover state.")
                        cover_state = CamTrackerThread.get_enclosure_cover_state(
                            config, state_lock, logger
                        )
                        logger.debug(f"Enclosure cover state: {cover_state}")

                        if config.camtracker.restart_if_cover_remains_closed and (
                            cover_state == "closed"
                        ):
                            t1 = time.time()
                            while True:
                                time.sleep(5)
                                state = interfaces.StateInterface.load_state(state_lock, logger)

                                # if rain detected in last 3 minutes -> cover can be closed
                                if (state.last_bad_weather_detection is not None) and (
                                    (time.time() - state.last_bad_weather_detection) < 180
                                ):
                                    logger.info("Enclosure cover is closed due to bad weather.")
                                    with interfaces.StateInterface.update_state(
                                        state_lock, logger
                                    ) as s:
                                        s.exceptions_state.clear_exception_subject(
                                            subject="Camtracker was started but cover is closed."
                                        )
                                    break

                                # if conditions changed -> no need to open cover
                                if not state.measurements_should_be_running:
                                    logger.info(
                                        "Measurements conditions have changed, hence no need to open cover."
                                    )
                                    with interfaces.StateInterface.update_state(
                                        state_lock, logger
                                    ) as s:
                                        s.exceptions_state.clear_exception_subject(
                                            subject="Camtracker was started but cover is closed."
                                        )
                                    break

                                # if enclosure cover is still closed after a good amount of waiting and no rain
                                # -> rain an exception
                                waiting_time = (config.general.seconds_per_core_iteration * 3) + 5
                                if (time.time() - t1) > waiting_time:
                                    logger.error(
                                        "Enclosure cover is closed even though, there is no rain. Stopping CamTracker."
                                    )
                                    with interfaces.StateInterface.update_state(
                                        state_lock, logger
                                    ) as s:
                                        s.exceptions_state.add_exception_state_item(
                                            types.ExceptionStateItem(
                                                origin="camtracker",
                                                subject="Camtracker was started but cover is closed.",
                                                details="Restarting CamTracker. No interaction needed.\n\nThis error might have been caused by the enclosures rain sensor being triggered long enough to cause the cover to be closed but too short for PYRA to read from rain sensor in time.",
                                            )
                                        )
                                    CamTrackerProgram.stop(config, logger)
                                    camtracker_is_running = False
                                    last_camtracker_start_time = None
                                    break

                        if cover_state == "open":
                            with interfaces.StateInterface.update_state(state_lock, logger) as s:
                                s.exceptions_state.clear_exception_subject(
                                    subject="Camtracker was started but cover is closed."
                                )

                # CLEAR EXCEPTIONS
                # besides the one about the cover not opening

                with interfaces.StateInterface.update_state(state_lock, logger) as s:
                    s.exceptions_state.current = [
                        e
                        for e in s.exceptions_state.current
                        if (
                            (e.origin != "camtracker")
                            or (e.subject == "Camtracker was started but cover is closed.")
                        )
                    ]

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                CamTrackerProgram.stop(config, logger)
                with interfaces.StateInterface.update_state(state_lock, logger) as s:
                    s.exceptions_state.add_exception(origin="camtracker", exception=e)
                logger.info("Sleeping 2 minutes")
                time.sleep(120)
                logger.info("Stopping thread")
                break

    @staticmethod
    def check_tracker_motor_positions(
        config: types.Config,
        logger: utils.Logger,
    ) -> Literal[
        "no logs",
        "logs too old",
        "offsets too high",
        "offsets are zero",
        "valid",
    ]:
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

        if (abs(tracker_position.azimuth_offset) > config.camtracker.motor_offset_threshold) or (
            abs(tracker_position.elevation_offset) > config.camtracker.motor_offset_threshold
        ):
            return "offsets too high"

        if (round(tracker_position.azimuth_offset, 6) == 0) or (
            round(tracker_position.elevation_offset, 6) == 0
        ):
            return "offsets are zero"

        return "valid"

    @staticmethod
    def get_enclosure_cover_state(
        config: types.Config,
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> Literal["not configured", "angle not reported", "open", "closed"]:
        """Checks whether the TUM PLC cover is open or closed. Returns
        "angle not reported" if the cover position has not beenreported
        by the PLC yet."""

        if config.tum_enclosure is not None:
            current_cover_angle = interfaces.StateInterface.load_state(
                state_lock, logger
            ).tum_enclosure_state.actors.current_angle

            if current_cover_angle is None:
                return "angle not reported"
            if 20 < ((current_cover_angle + 360) % 360) < 340:
                return "open"
            else:
                return "closed"
        elif config.aemet_enclosure is not None:
            if (
                interfaces.StateInterface.load_state(
                    state_lock, logger
                ).aemet_enclosure_state.pretty_cover_status
                == "open"
            ):
                return "open"
            else:
                return "closed"
        else:
            return "not configured"

    @staticmethod
    def test_setup(
        config: types.Config,
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> None:
        """Function to test the functonality of this module. Starts up
        CamTracker to initialize the tracking mirrors. Then moves mirrors
        back to parking position and shuts dosn CamTracker."""

        assert not CamTrackerProgram.is_running(), (
            "This test cannot be run if CamTracker is already running"
        )
        CamTrackerProgram.start(config, state_lock, logger)
        time.sleep(2)
        CamTrackerProgram.stop(config, logger)
