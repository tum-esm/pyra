import os
import sys
import threading
import time
from typing import Any, Optional
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
            self.teardown()

        self.client = brukeropus.control.dde.DDEClient("Opus", "System")
        time.sleep(0.5)
        if not self.is_working():
            raise RuntimeError("DDE connection to OPUS is not working")

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


class OpusProgram:
    """TODO: docstring"""
    @staticmethod
    def start(config: types.Config) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        interfaces.ActivityHistoryInterface.add_datapoint(opus_startups=1)

        # works only >= python3.10 because it requires the "cwd" argument
        assert sys.platform == "win32", f"this function cannot be run on platform {sys.platform}"
        assert sys.version_info.major >= 3 and sys.version_info.minor >= 10, "this function requires python >= 3.10"

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
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass

        return False

    @staticmethod
    def stop(dde_connection: Optional[DDEConnection] = None) -> None:
        """Closes OPUS via DDE/force kills it via psutil. If no DDEConnection
        is provided, the function will force kill OPUS right away."""

        if (dde_connection is not None) and dde_connection.is_working():
            assert sys.platform == "win32", f"this function cannot be run on platform {sys.platform}"

            logger.info(f"Requesting to stop OPUS via DDE")
            dde_connection.request("CLOSE_OPUS")

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
    """TODO: docstring"""
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
        current_experiment_path: Optional[str] = None
        current_macro_path: Optional[str] = None
        dde_connection = DDEConnection()

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
                    dde_connection.teardown()
                    dde_connection.setup()
                    continue
                if (not opus_should_be_running) and OpusProgram.is_running():
                    logger.info("OPUS should not be running, stopping OPUS")
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
                    dde_connection.request(f"LOAD_EXPERIMENT {config.opus.experiment_path.root}")
                    time.sleep(5)
                    current_experiment_path = config.opus.experiment_path.root
                    logger.info(f"Experiment file {current_experiment_path} was loaded")

                # DETERMINE WHETHER MEASUREMENTS SHOULD BE RUNNING

                state = interfaces.StateInterface.load_state()
                measurements_should_be_running = state.measurements_should_be_running == True
                if measurements_should_be_running:
                    if state.plc_state.actors.current_angle is not None:
                        cover_is_open = 20 < state.plc_state.actors.current_angle < 340
                        if not cover_is_open:
                            measurements_should_be_running = False

                # STARTING MACRO

                if measurements_should_be_running:
                    if current_macro_path is None:
                        logger.info("Starting macro")
                        dde_connection.request(f"RUN_MACRO {config.opus.macro_path.root}")
                        time.sleep(5)
                        current_macro_path = config.opus.macro_path.root
                        logger.info(f"Macro file {current_macro_path} was started")
                    else:
                        if config.opus.macro_path.root != current_macro_path:
                            logger.info("Macro file has changed, stopping macro")
                            dde_connection.request(
                                f"KILL_MACRO {os.path.basename(current_macro_path)}"
                            )
                            time.sleep(5)
                            logger.info("Starting new macro")
                            dde_connection.request(f"RUN_MACRO {config.opus.macro_path.root}")
                            time.sleep(5)
                            current_macro_path = config.opus.macro_path.root
                            logger.info(f"Macro file {current_macro_path} was loaded")

                # STOPPING MACRO

                if (not measurements_should_be_running) and (current_macro_path is not None):
                    logger.info("Stopping macro")
                    dde_connection.request(f"KILL_MACRO {os.path.basename(current_macro_path)}")
                    time.sleep(5)
                    current_macro_path = None
                    logger.info(f"Stopped Macro {current_macro_path}")

                # SLEEP

                t2 = time.time()
                sleep_time = 30 - (t2 - t1)
                if sleep_time > 0:
                    logger.info(f"Sleeping {sleep_time} seconds")
                    time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                logger.info("Sleeping 2 minutes")
                time.sleep(120)
                logger.info("Stopping thread")
                break

    @staticmethod
    def test_setup(config: types.Config) -> None:
        assert sys.platform == "win32", f"this function cannot be run on platform {sys.platform}"
        assert not OpusProgram.is_running(), "this test cannot be run if OPUS is already running"

        OpusProgram.start(config)

        dde_connection = DDEConnection()
        dde_connection.setup()

        dde_connection.request(f"LOAD_EXPERIMENT {config.opus.experiment_path.root}")
        time.sleep(5)

        dde_connection.request(f"RUN_MACRO {config.opus.macro_path.root}")
        time.sleep(10)

        # TODO: we could use "MACRO_RESULTS <MacroID>" to test whether
        #       the macro is actually running once we figure out
        #       https://github.com/tum-esm/pyra/issues/124

        dde_connection.request(f"KILL_MACRO {os.path.basename(config.opus.macro_path.root)}")
        time.sleep(10)

        OpusProgram.stop(dde_connection)
