import traceback
from typing import Optional
import os
import threading
import time
import psutil
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import types, utils, interfaces
import brukeropus.control.dde

logger = utils.Logger(origin="opus")


class DDEConnection:
    """Class for handling DDE connections to OPUS."""
    def __init__(self) -> None:
        self.client: Optional[brukeropus.control.dde.DDEClient] = None

    def setup(self) -> None:
        """Set up a new DDE connection to OPUS. Tear down the 
        old connection if it exists."""

        if self.client is not None:
            logger.info("Destroying old DDE connection")
            self.teardown()
            time.sleep(0.5)

        logger.info("Setting up new DDE connection")
        self.client = brukeropus.control.dde.DDEClient("Opus", "System")
        time.sleep(0.5)
        if not self.is_working():
            raise RuntimeError("DDE connection to OPUS is not working")
        answer = self.request("GET_VERSION_EXTENDED")
        logger.info(f"Connected to OPUS version {answer[0]}")

    def is_working(self) -> bool:
        """Check if the DDE connection is working."""
        if self.client is None:
            return False
        answer = self.request("COMMAND_SAY hello")
        return (answer[0] == "OK") and (answer[1] == "hello")

    def teardown(self) -> None:
        """Tear down the current DDE connection."""
        if self.client is not None:
            logger.info("Destroying DDE connection")
            del self.client
            self.client = None
        else:
            logger.info("No DDE connection to tear down")

    def request(
        self,
        command: str,
        expected_answer: Optional[list[str]] = None,
        expect_ok: Optional[bool] = None,
        timeout: float = 5
    ) -> list[str]:
        """Send a request to the OPUS DDE server. Run `setup()` if the 
        connection is not yet established."""

        if self.client is None:
            self.setup()
        raw_answer: bytes = self.client.request(command, timeout=int(timeout * 1000))
        answer = raw_answer.decode("utf-8").strip("\n").split("\n\n")
        if expected_answer is not None:
            if answer != expected_answer:
                raise RuntimeError(
                    f"Unexpected answer from OPUS: {answer}, expected {expected_answer}"
                )
        if expect_ok is not None:
            assert answer[0] == "OK"

    def get_main_thread_id(self) -> int:
        """Get the main thread ID of OPUS."""
        answer = self.request("FIND_FUNCTION 0", expect_ok=True)
        return int(answer[1])

    def macro_is_running(self, macro_id: int) -> bool:
        answer = self.request(f'MACRO_RESULTS {macro_id}', expect_ok=True)
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
            "MeasureReference", "MeasureSample", "MeasureRepeated", "MeasureRapidTRS",
            "MeasureStepScanTrans", "UserDialog", "Baseline", "PeakPick", "Timer", "SendCommand"
        ]

        # check twice for any thread that is executing a common function
        for function in common_functions:
            answer = self.request(f'FIND_FUNCTION {function}')
            if len(answer) == 2:
                active_thread_ids.add(int(answer[1]))
        time.sleep(3)
        for function in common_functions:
            answer = self.request(f'FIND_FUNCTION {function}')
            if len(answer) == 2:
                active_thread_ids.add(int(answer[1]))

        # the main thread always runs some common functions for some reason
        if main_thread_id in active_thread_ids:
            active_thread_ids.remove(main_thread_id)

        # if there is any thread that is not the main thread, then a macro is running
        return len(active_thread_ids) > 0

    def get_loaded_experiment(self) -> str:
        self.request('OPUS_PARAMETERS', expect_ok=True)
        xpp_answer = self.request('READ_PARAMETER XPP', expect_ok=True)
        exp_answer = self.request('READ_PARAMETER EXP', expect_ok=True)
        return os.path.join(xpp_answer[1], exp_answer[1])

    def load_experiment(self, experiment_path: str) -> None:
        """Load an experiment file into OPUS."""
        self.request(f"LOAD_EXPERIMENT {experiment_path}", expect_ok=True)

    def start_macro(self, macro_path: str) -> int:
        """Start a macro in OPUS. Returns the macro ID."""

        answer = self.request(f"RUN_MACRO {macro_path}", expect_ok=True)
        return int(answer[1])

    def stop_macro(self, macro_path: str, macro_id: int) -> None:
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
    def start(config: types.Config) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        interfaces.ActivityHistoryInterface.add_datapoint(opus_startups=1)

        os.startfile(  # type: ignore
            os.path.basename(config.opus.executable_path.root),
            cwd=os.path.dirname(config.opus.executable_path.root),
            arguments=f"/LANGUAGE=ENGLISH /DIRECTLOGINPASSWORD={config.opus.username}@{config.opus.password}",
            show_cmd=2,
        )
        tum_esm_utils.timing.wait_for_condition(
            is_successful=OpusProgram.is_running,
            timeout_message="OPUS.exe did not start within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=8,
        )

    @staticmethod
    def is_running() -> bool:
        """Checks if OPUS is already running by searching for processes with
        the executable `opus.exe` or `OpusCore.exe`

        Returns: `True` if Application is currently running and `False` if not."""

        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    return True
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess, IndexError):
                pass

        return False

    @staticmethod
    def stop(dde_connection: Optional[DDEConnection] = None) -> None:
        """Closes OPUS via DDE/force kills it via psutil. If no DDEConnection
        is provided, the function will force kill OPUS right away."""

        try:
            if (dde_connection is not None) and dde_connection.is_working():
                logger.info(f"Requesting to stop OPUS via DDE")
                dde_connection.request("UnloadAll()", expect_ok=True)
                dde_connection.request("CLOSE_OPUS", expect_ok=True)

                logger.info(f"Waiting for OPUS to close gracefully")
                try:
                    tum_esm_utils.timing.wait_for_condition(
                        is_successful=lambda: not OpusProgram.is_running(),
                        timeout_message="OPUS.exe did not stop within 60 seconds.",
                        timeout_seconds=60,
                        check_interval_seconds=4,
                    )
                    logger.info("OPUS.exe stopped successfully.")
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


class OpusControlThread(AbstractThread):
    """Thread for controlling OPUS. This thread starts/stops the OPUS executable
    whenever it is not running.
    
    TODO"""
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""
        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=OpusControlThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        current_experiment_filepath: Optional[str] = None
        current_macro_filepath: Optional[str] = None
        current_macro_id: Optional[int] = None
        dde_connection = DDEConnection()

        logger.info("Loading state file")
        state = interfaces.StateInterface.load_state()
        thread_start_time = time.time()

        if OpusProgram.is_running():
            logger.info("OPUS is already running")

            dde_connection.setup()
            if dde_connection.some_macro_is_running():
                logger.info("Some macro is already running")

                if state.opus_state.macro_id is None:
                    logger.info("Macro ID is unknown, stopping OPUS entirely")
                    OpusProgram.stop(dde_connection)
                else:
                    if dde_connection.macro_is_running(state.opus_state.macro_id):
                        logger.info("The Macro started by Pyra is still running, nothing to do")
                        current_experiment_filepath = dde_connection.get_loaded_experiment()
                        current_macro_filepath = state.opus_state.macro_filepath
                        current_macro_id = state.opus_state.macro_id

                    else:
                        logger.info(
                            "The Macro running in OPUS is not the one started by Pyra, stopping OPUS entirely"
                        )
                        OpusProgram.stop(dde_connection)
            else:
                current_experiment_filepath = dde_connection.get_loaded_experiment()

        with interfaces.StateInterface.update_state() as state:
            state.opus_state.experiment_filepath = current_experiment_filepath
            state.opus_state.macro_filepath = current_macro_filepath
            state.opus_state.macro_id = current_macro_id

        while True:
            try:
                logger.info("Loading configuration file")
                config = types.Config.load()
                t1 = time.time()

                # START AND OPUS

                opus_should_be_running = (
                    utils.Astronomy.get_current_sun_elevation(config)
                    >= config.general.min_sun_elevation
                )
                if opus_should_be_running and (not OpusProgram.is_running()):
                    logger.info("OPUS should be running, starting OPUS")
                    OpusProgram.start(config)
                    dde_connection.setup()
                    continue
                if (not opus_should_be_running) and OpusProgram.is_running():
                    logger.info("OPUS should not be running, stopping OPUS")
                    if current_macro_id is not None:
                        if dde_connection.macro_is_running(current_macro_id):
                            logger.info("Stopping macro")
                            dde_connection.stop_macro(current_macro_filepath, current_macro_id)
                            current_macro_filepath = None
                            current_macro_id = None
                            with interfaces.StateInterface.update_state() as state:
                                state.opus_state.macro_filepath = None
                                state.opus_state.macro_id = None
                    OpusProgram.stop(dde_connection)
                    dde_connection.teardown()
                    continue

                # IDLE AT NIGHT

                if not opus_should_be_running:
                    logger.info("Sleeping 3 minutes")
                    time.sleep(180)
                    continue

                # LOAD EXPERIMENT

                if config.opus.experiment_path.root != current_experiment_path:
                    if current_experiment_path is None:
                        logger.info("Loading experiment")
                    else:
                        logger.info("Experiment file has changed, loading new experiment")
                    dde_connection.load_experiment(config.opus.experiment_path.root)
                    current_experiment_path = config.opus.experiment_path.root
                    logger.info(f"Experiment file {current_experiment_path} was loaded")
                    with interfaces.StateInterface.update_state() as state:
                        state.opus_state.experiment_filepath = current_experiment_path

                # DETERMINE WHETHER MEASUREMENTS SHOULD BE RUNNING

                state = interfaces.StateInterface.load_state()
                measurements_should_be_running = state.measurements_should_be_running == True
                if measurements_should_be_running:
                    if state.plc_state.actors.current_angle is not None:
                        cover_is_open = 20 < state.plc_state.actors.current_angle < 340
                        if not cover_is_open:
                            measurements_should_be_running = False

                # CHECK IF MACRO HAS CRASHED

                if thread_start_time < (time.time() - 60):
                    if current_macro_filepath is not None:
                        assert current_macro_id is not None, "this should not happen"
                        if not dde_connection.macro_is_running(current_macro_id):
                            raise RuntimeError("Macro has stopped/crashed")

                # STARTING MACRO

                if measurements_should_be_running:
                    if current_macro_filepath is None:
                        logger.info("Starting macro")
                        current_macro_filepath = config.opus.macro_path.root
                        current_macro_id = dde_connection.start_macro(current_macro_filepath)
                        logger.info(f"Successfully started Macro {current_macro_filepath}")
                    else:
                        if config.opus.macro_path.root != current_macro_filepath:
                            logger.info("Macro file has changed, stopping macro")
                            dde_connection.stop_macro(current_macro_filepath, current_macro_id)
                            current_macro_filepath = None
                            current_macro_id = None
                            logger.info("Successfully stopped Macro")

                # STOPPING MACRO

                if (not measurements_should_be_running) and (current_macro_filepath is not None):
                    logger.info("Stopping macro")
                    dde_connection.stop_macro(current_macro_filepath, current_macro_id)
                    current_macro_filepath = None
                    current_macro_id = None
                    logger.info(f"Successfully stopped Macro")

                # UPDATING STATE

                clear_issues = thread_start_time < (time.time() - 180)
                if not clear_issues:
                    logger.info(
                        "Waiting for thread to run for 3 minutes before clearing exceptions"
                    )

                with interfaces.StateInterface.update_state() as state:
                    state.opus_state.macro_filepath = current_macro_filepath
                    state.opus_state.macro_id = current_macro_id

                    # TODO: turn this into a function
                    if clear_issues:
                        state.current_exceptions = [
                            e for e in state.current_exceptions if (e.origin != "opus")
                        ]

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, 30 - (t2 - t1))
                logger.info(f"Sleeping {sleep_time} seconds")
                time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                OpusProgram.stop(dde_connection)
                with interfaces.StateInterface.update_state() as state:
                    state.opus_state.macro_filepath = None
                    state.opus_state.macro_id = None
                    # TODO: turn this into a function
                    state.current_exceptions.append(
                        types.ExceptionStateItem(
                            origin="opus",
                            subject=type(e).__name__,
                            details="\n".join(traceback.format_exception(e)),
                        )
                    )
                logger.info("Sleeping 2 minutes")
                time.sleep(120)
                logger.info("Stopping thread")
                break

    @staticmethod
    def test_setup(config: types.Config) -> None:
        OpusProgram.start(config)

        dde_connection = DDEConnection()
        dde_connection.setup()

        dde_connection.load_experiment(config.opus.experiment_path.root)
        time.sleep(5)

        macro_id = dde_connection.start_macro(config.opus.macro_path.root)
        time.sleep(5)
        assert dde_connection.macro_is_running(macro_id), "Macro is not running"

        dde_connection.stop_macro(config.opus.macro_path.root)
        time.sleep(2)

        OpusProgram.stop(dde_connection)
