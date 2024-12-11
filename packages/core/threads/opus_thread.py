import datetime
import os
import threading
import time
from typing import Any, Optional

import numpy as np
import psutil
import tum_esm_utils

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread

ORIGIN = "opus"


class DDEConnection:
    """Class for handling DDE connections to OPUS."""

    def __init__(self, logger: utils.Logger) -> None:
        import brukeropus.control.dde

        self.client: Optional[brukeropus.control.dde.DDEClient] = None
        self.logger = logger

    def setup(self) -> None:
        """Set up a new DDE connection to OPUS. Tear down the
        old connection if it exists."""
        import brukeropus.control.dde

        if self.client is not None:
            self.logger.info("Destroying old DDE connection")
            self.teardown()
            time.sleep(0.5)

        self.logger.info("Setting up new DDE connection")
        self.client = brukeropus.control.dde.DDEClient("Opus", "System")
        time.sleep(0.5)
        if not self.is_working():
            raise RuntimeError("DDE connection to OPUS is not working")
        answer = self.request("GET_VERSION_EXTENDED")
        self.logger.info(f"Connected to OPUS version {answer[0]}")

    def is_working(self) -> bool:
        """Check if the DDE connection is working."""
        if self.client is None:
            return False
        answer = self.request("COMMAND_SAY hello")
        return (answer[0] == "OK") and (answer[1] == "hello")

    def teardown(self) -> None:
        """Tear down the current DDE connection."""
        if self.client is not None:
            self.logger.info("Destroying DDE connection")
            del self.client
            self.client = None
        else:
            self.logger.info("No DDE connection to tear down")

    def request(
        self,
        command: str,
        expected_answer: Optional[list[str]] = None,
        expect_ok: Optional[bool] = None,
        timeout: float = 5,
    ) -> list[str]:
        """Send a request to the OPUS DDE server. Run `setup()` if the
        connection is not yet established."""

        if self.client is None:
            self.setup()
        raw_answer: bytes = self.client.request(  # type: ignore
            command, timeout=int(timeout * 1000)
        )
        answer = raw_answer.decode("utf-8").strip("\n").split("\n\n")
        if expected_answer is not None:
            if answer != expected_answer:
                raise RuntimeError(
                    f"Unexpected answer from OPUS: {answer}, expected {expected_answer}"
                )
        if expect_ok is not None:
            assert answer[0] == "OK"

        return answer

    def get_main_thread_id(self) -> int:
        """Get the main thread ID of OPUS."""
        answer = self.request("FIND_FUNCTION 0", expect_ok=True)
        return int(answer[1])

    def macro_is_running(self, macro_id: int) -> bool:
        answer = self.request(f"MACRO_RESULTS {macro_id}", expect_ok=True)
        return int(answer[1]) == 0

    def some_macro_is_running(self) -> bool:
        """Check if any macro is currently running in OPUS.

        In theory, we could also check whether the correct macro is running using
        `READ_PARAMETER MPT` and `READ_PARAMETER MFN`. However, these variables do
        not seem to be updated right away, so we cannot rely on them."""

        main_thread_id = self.get_main_thread_id()
        active_thread_ids: set[int] = set()

        # some common functions executed inside Macro routines that take some time
        common_functions = [
            "MeasureReference",
            "MeasureSample",
            "MeasureRepeated",
            "MeasureRapidTRS",
            "MeasureStepScanTrans",
            "UserDialog",
            "Baseline",
            "PeakPick",
            "Timer",
            "SendCommand",
        ]

        # check twice for any thread that is executing a common function
        for function in common_functions:
            answer = self.request(f"FIND_FUNCTION {function}")
            if len(answer) == 2:
                active_thread_ids.add(int(answer[1]))
        time.sleep(3)
        for function in common_functions:
            answer = self.request(f"FIND_FUNCTION {function}")
            if len(answer) == 2:
                active_thread_ids.add(int(answer[1]))

        # the main thread always runs some common functions for some reason
        if main_thread_id in active_thread_ids:
            active_thread_ids.remove(main_thread_id)

        # if there is any thread that is not the main thread, then a macro is running
        return len(active_thread_ids) > 0

    def get_loaded_experiment(self) -> str:
        self.request("OPUS_PARAMETERS", expect_ok=True)
        xpp_answer = self.request("READ_PARAMETER XPP", expect_ok=True)
        exp_answer = self.request("READ_PARAMETER EXP", expect_ok=True)
        return os.path.join(xpp_answer[1], exp_answer[1])

    def load_experiment(self, experiment_path: str) -> None:
        """Load an experiment file into OPUS."""
        self.request(f"LOAD_EXPERIMENT {experiment_path}", expect_ok=True)

    def start_macro(self, macro_path: str) -> int:
        """Start a macro in OPUS. Returns the macro ID."""

        answer = self.request(f"RUN_MACRO {macro_path}", expect_ok=True)
        return int(answer[1])

    def stop_macro(self, macro_id: int, macro_path: str) -> None:
        """Stop a macro in OPUS."""
        self.request(f"KILL_MACRO {os.path.basename(macro_path)}", expect_ok=True)
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: not self.macro_is_running(macro_id),
            timeout_message="Macro did not stop within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=9,
        )


class OpusProgram:
    """Class for starting and stopping OPUS."""

    @staticmethod
    def start(config: types.Config, logger: utils.Logger) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        interfaces.ActivityHistoryInterface.add_datapoint(opus_startups=1)

        logger.info("Starting OPUS")
        os.startfile(  # type: ignore
            os.path.basename(config.opus.executable_path.root),
            cwd=os.path.dirname(config.opus.executable_path.root),
            arguments=f"/LANGUAGE=ENGLISH /DIRECTLOGINPASSWORD={config.opus.username}@{config.opus.password}",
            show_cmd=2,
        )
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: OpusProgram.is_running(logger),
            timeout_message="OPUS.exe did not start within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=8,
        )
        logger.info("Successfully started OPUS")

    @staticmethod
    def is_running(logger: utils.Logger) -> bool:
        """Checks if OPUS is already running by searching for processes with
        the executable `opus.exe` or `OpusCore.exe`."""

        logger.debug("Checking if OPUS is running")
        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    return True
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess, IndexError):
                pass

        return False

    @staticmethod
    def stop(logger: utils.Logger, dde_connection: Optional[DDEConnection] = None) -> None:
        """Closes OPUS via DDE/force kills it via psutil. If no DDEConnection
        is provided, the function will force kill OPUS right away."""

        try:
            if (dde_connection is not None) and dde_connection.is_working():
                logger.info("Requesting to stop OPUS via DDE")
                dde_connection.request("UnloadAll()", expect_ok=True)
                dde_connection.request("CLOSE_OPUS", expect_ok=True)

                logger.info("Waiting for OPUS to close gracefully")
                try:
                    tum_esm_utils.timing.wait_for_condition(
                        is_successful=lambda: not OpusProgram.is_running(logger),
                        timeout_message="OPUS.exe did not stop within 60 seconds.",
                        timeout_seconds=60,
                        check_interval_seconds=4,
                    )
                    logger.info("Successfully stopped OPUS")
                    return
                except TimeoutError:
                    logger.warning("OPUS.exe did not stop gracefully within 60 seconds.")
        except Exception as e:
            logger.exception(e)
            logger.error("Could not stop OPUS via DDE")

        logger.info("Force killing OPUS")
        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    p.kill()
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass
        logger.info("Successfully force killed OPUS")


class OpusThread(AbstractThread):
    """Thread for controlling OPUS.

    * starts/stops the OPUS executable whenever it is not running and `config.general.min_sun_elevation` is reached
    * starts/stops the macro whenever measurements should be running
    * raises an exception if the macro crashes unexpectedly
    * on startup, detects if OPUS is already running an unidentified macro - if so, stops OPUS entirely
    * stores the macro ID so if Pyra Core or this thread crashes, it can continue using the same macro thread
    * Pings the EM27 every 5 minutes to check if it is still connected
    """

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""
        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=OpusThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        logger = utils.Logger(origin=ORIGIN)

        current_experiment: Optional[str] = None  # filepath
        current_macro: Optional[tuple[int, str]] = None  # id and filepath
        dde_connection = DDEConnection(logger)

        logger.info("Loading state file")
        state = interfaces.StateInterface.load_state()

        thread_start_time = time.time()
        last_successful_ping_time = time.time()
        last_measurement_start_time: Optional[float] = None
        last_peak_positioning_time: Optional[float] = None

        # CHECK IF OPUS IS ALREADY RUNNING
        # ONLY RESTART IF THERE IS AN UNIDENTIFIED MACRO RUNNING

        if OpusProgram.is_running(logger):
            logger.info("OPUS is already running")

            dde_connection.setup()
            current_experiment = dde_connection.get_loaded_experiment()

            if dde_connection.some_macro_is_running():
                logger.info("Some macro is already running")
                mid = state.opus_state.macro_id
                mfp = state.opus_state.macro_filepath

                if (mid is None) or (mfp is None) or (not dde_connection.macro_is_running(mid)):
                    logger.info("Macro ID is unknown, stopping OPUS entirely")
                    OpusProgram.stop(logger, dde_connection)
                else:
                    logger.info("The Macro started by Pyra is still running, nothing to do")
                    current_macro = (mid, mfp)
                    last_measurement_start_time = time.time()

        with interfaces.StateInterface.update_state() as state:
            state.opus_state.experiment_filepath = current_experiment
            state.opus_state.macro_id = None if current_macro is None else current_macro[0]
            state.opus_state.macro_filepath = None if current_macro is None else current_macro[1]

        while True:
            try:
                logger.info("Loading configuration file")
                config = types.Config.load()
                t1 = time.time()

                opus_should_be_running = (
                    utils.Astronomy.get_current_sun_elevation(config)
                    >= config.general.min_sun_elevation
                )

                # START OPUS

                if opus_should_be_running and (not OpusProgram.is_running(logger)):
                    logger.info("OPUS should be running, starting OPUS")
                    OpusProgram.start(config, logger)
                    dde_connection.setup()
                    continue

                # STOP OPUS

                if (not opus_should_be_running) and OpusProgram.is_running(logger):
                    logger.info("OPUS should not be running, stopping OPUS")
                    if current_macro is None:
                        logger.info("No macro to stop")
                    else:
                        if dde_connection.macro_is_running(current_macro[0]):
                            logger.info("Stopping macro")
                            dde_connection.stop_macro(*current_macro)
                            current_macro = None
                            with interfaces.StateInterface.update_state() as state:
                                state.opus_state.macro_id = None
                                state.opus_state.macro_filepath = None

                    OpusProgram.stop(logger, dde_connection)
                    dde_connection.teardown()
                    continue

                # IDLE AT NIGHT

                if not opus_should_be_running:
                    logger.info("Sleeping 3 minutes")
                    time.sleep(180)
                    continue

                # LOAD CORRECT EXPERIMENT

                if config.opus.experiment_path.root != current_experiment:
                    if current_experiment is None:
                        logger.info("Loading experiment")
                    else:
                        logger.info("Experiment file has changed, loading new experiment")
                    dde_connection.load_experiment(config.opus.experiment_path.root)
                    current_experiment = config.opus.experiment_path.root
                    logger.info(f"Experiment file {current_experiment} was loaded")
                    with interfaces.StateInterface.update_state() as state:
                        state.opus_state.experiment_filepath = current_experiment

                # DETERMINE WHETHER MEASUREMENTS SHOULD BE RUNNING

                state = interfaces.StateInterface.load_state()
                measurements_should_be_running = bool(state.measurements_should_be_running)
                if measurements_should_be_running:
                    # only measure if cover is open
                    if state.tum_enclosure_state.actors.current_angle is not None:
                        measurements_should_be_running = (
                            20 < state.tum_enclosure_state.actors.current_angle < 340
                        )

                # PING EM27 EVERY 5 MINUTES

                if measurements_should_be_running:
                    if last_successful_ping_time < (time.time() - 300):
                        logger.info("Pinging EM27")
                        tum_esm_utils.timing.wait_for_condition(
                            is_successful=lambda: os.system("ping -n 3 " + config.opus.em27_ip.root)
                            == 0,
                            timeout_seconds=90,
                            timeout_message="EM27 did not respond to ping within 90 seconds.",
                            check_interval_seconds=9,
                        )
                        last_successful_ping_time = time.time()
                        logger.info("Successfully pinged EM27")

                # STARTING MACRO

                if measurements_should_be_running and (current_macro is None):
                    logger.info("Starting macro")
                    mid = dde_connection.start_macro(config.opus.macro_path.root)
                    current_macro = (mid, config.opus.macro_path.root)
                    logger.info(f"Successfully started Macro {current_macro[1]}")
                    last_measurement_start_time = time.time()

                # STOPPING MACRO WHEN MACRO FILE CHANGES

                if measurements_should_be_running and (current_macro is not None):
                    if config.opus.macro_path.root != current_macro[1]:
                        logger.info("Macro file has changed, stopping macro")
                        dde_connection.stop_macro(*current_macro)
                        current_macro = None
                        last_measurement_start_time = None
                        logger.info("Successfully stopped Macro")

                # STOPPING MACRO

                if (not measurements_should_be_running) and (current_macro is not None):
                    logger.info("Stopping macro")
                    dde_connection.stop_macro(*current_macro)
                    current_macro = None
                    last_measurement_start_time = None
                    logger.info("Successfully stopped Macro")

                # CHECK IF MACRO HAS CRASHED

                if current_macro is not None:
                    assert last_measurement_start_time is not None
                    if (time.time() - last_measurement_start_time) > 60:
                        if dde_connection.macro_is_running(current_macro[0]):
                            logger.debug("Macro is running as expected")
                        else:
                            raise RuntimeError("Macro has stopped/crashed")

                # POSSIBLY SET PEAK POSITION

                if config.opus.automatic_peak_positioning and (last_peak_positioning_time is None):
                    if current_macro is not None:
                        last_em27_powerup_time = (
                            interfaces.EM27Interface.get_last_powerup_timestamp(config.opus.em27_ip)
                        )
                        if last_em27_powerup_time is None:
                            logger.info("Could not determine last powerup time of EM27")
                        elif (time.time() - last_em27_powerup_time) < 180:
                            logger.info(
                                "EM27 was powered up less than 3 minutes ago, skipping peak positioning"
                            )
                        else:
                            logger.info("Trying to set peak position")
                            try:
                                OpusThread.set_peak_position(config, logger)
                                last_peak_positioning_time = time.time()
                            except (ValueError, RuntimeError) as e:
                                logger.error(f"Could not set peak position: {e}")

                # DETECT WHEN EM27 HAD A POWER CYCLE SINCE LAST PEAK POSITION CHECK

                if config.opus.automatic_peak_positioning and (
                    last_peak_positioning_time is not None
                ):
                    last_em27_powerup_time = interfaces.EM27Interface.get_last_powerup_timestamp(
                        config.opus.em27_ip
                    )
                    if last_em27_powerup_time is None:
                        logger.info("Could not determine last powerup time of EM27")
                    elif last_peak_positioning_time < (last_em27_powerup_time + 175):
                        logger.info(
                            "EM27 had a power cycle since the last peak positioning, repeating peak positioning in the next loop"
                        )
                        last_peak_positioning_time = None

                # UPDATING STATE

                clear_issues = (time.time() - thread_start_time) >= 180
                if not clear_issues:
                    logger.info(
                        "Waiting for thread to run for 3 minutes before clearing exceptions"
                    )

                with interfaces.StateInterface.update_state() as state:
                    if current_macro is None:
                        state.opus_state.macro_id = None
                        state.opus_state.macro_filepath = None
                    else:
                        state.opus_state.macro_id = current_macro[0]
                        state.opus_state.macro_filepath = current_macro[1]
                    if clear_issues:
                        state.exceptions_state.clear_exception_origin(ORIGIN)

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, 30 - (t2 - t1))
                logger.info(f"Sleeping {sleep_time} seconds")
                time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                OpusProgram.stop(logger, dde_connection)
                with interfaces.StateInterface.update_state() as state:
                    state.opus_state.macro_id = None
                    state.opus_state.macro_filepath = None
                    state.exceptions_state.add_exception(origin=ORIGIN, exception=e)
                logger.info("Sleeping 2 minutes")
                time.sleep(120)
                logger.info("Stopping thread")
                break

    @staticmethod
    def test_setup(config: types.Config, logger: utils.Logger) -> None:
        OpusProgram.start(config, logger)

        dde_connection = DDEConnection(logger)
        dde_connection.setup()

        dde_connection.load_experiment(config.opus.experiment_path.root)
        time.sleep(5)

        macro_id = dde_connection.start_macro(config.opus.macro_path.root)
        time.sleep(5)
        assert dde_connection.macro_is_running(macro_id), "Macro is not running"

        dde_connection.stop_macro(macro_id, config.opus.macro_path.root)
        time.sleep(2)

        OpusProgram.stop(logger, dde_connection)

    @staticmethod
    def set_peak_position(config: types.Config, logger: utils.Logger) -> None:
        """Set the peak position based on the latest OPUS files.

        The function throws a `ValueError` or `RuntimeError` if the peak position cannot be set."""

        # find newest three readable OPUS files
        today = datetime.date.today()
        ifg_file_directory = (
            config.opus.interferogram_path.replace("%Y", f"{today.year}:4d")
            .replace("%y", f"{today.year % 100}:2d")
            .replace("%m", f"{today.month}:2d")
            .replace("%d", f"{today.day}:2d")
        )
        if not os.path.exists(ifg_file_directory):
            raise ValueError(f"Directory {ifg_file_directory} does not exist")

        # Only consider files created within the last 10 minutes
        # and at least 1 minute after the last powerup of the EM27
        last_em27_powerup_time = interfaces.EM27Interface.get_last_powerup_timestamp(
            config.opus.em27_ip
        )
        if last_em27_powerup_time is None:
            raise RuntimeError("Could not determine last powerup time of EM27")
        time_since_powerup = time.time() - last_em27_powerup_time
        most_recent_files = utils.find_most_recent_files(
            ifg_file_directory,
            time_limit=min(600, time_since_powerup - 60),
            time_indicator="created",
        )

        # compute peak position of these files using the first channel
        latest_peak_positions: list[int] = []
        for f in most_recent_files:
            try:
                ifg = tum_esm_utils.opus.OpusFile.read(f, read_all_channels=False).interferogram
                assert ifg is not None
                fwd_pass: np.ndarray[Any, Any] = ifg[0][: ifg.shape[1] // 2]
                assert len(fwd_pass) == 114256, "Interferogram has wrong length"
                computed_peak = int(np.argmax(fwd_pass))
                ifg_center = fwd_pass.shape[0] // 2
                assert abs(computed_peak - ifg_center) < 200, "Peak is too far off"
                latest_peak_positions.append(computed_peak)
            except:
                pass
            if len(latest_peak_positions) == 3:
                break
        if len(latest_peak_positions) < 3:
            raise ValueError(
                f"Could not read enough peak positions from interferograms (read {len(latest_peak_positions)}"
            )

        # compare the peak positions to each other
        d01 = abs(latest_peak_positions[0] - latest_peak_positions[1])
        d02 = abs(latest_peak_positions[0] - latest_peak_positions[2])
        d12 = abs(latest_peak_positions[1] - latest_peak_positions[2])
        if max(d01, d02, d12) > 10:
            raise ValueError(f"Peak positions are too far apart: {latest_peak_positions}")
        new_peak_position = round(sum(latest_peak_positions) / 3)

        # set new peak position
        current_peak_position = interfaces.EM27Interface.get_peak_position(config.opus.em27_ip)
        if current_peak_position is None:
            raise RuntimeError("Could not read the current peak position")

        logger.info(f"Updating peak position from {current_peak_position} to {new_peak_position}")
        interfaces.EM27Interface.set_peak_position(config.opus.em27_ip, new_peak_position)
