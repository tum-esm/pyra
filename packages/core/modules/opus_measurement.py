import os
import sys
import time
from typing import Any
from packages.core import types, utils, interfaces

# these imports are provided by pywin32
_win32ui: Any = None
_dde: Any = None
if sys.platform == "win32":
    import win32ui as _win32ui  # type: ignore
    import dde as _dde  # type: ignore

logger = utils.Logger(origin="opus-measurement")


class OpusMeasurement:
    """OPUS Measurements manages the FTIR spectrometer measurement
    software OPUS. It allows to remotely communicate with OPUS
    via a DDE connection and trigger different commands.

    OPUS needs an experiment file and can perform continious
    measurements with parameters passed by a macro file. These
    files can be loaded via commands over the active DDE connection.

    During the day it makes sure that OPUS up and running and
    reloads the latest experiment if it was changed by the operator.
    During night OPUS is shut down to reset after a full day of
    measurements. Day and night is defined by the set sun angle
    in the config.

    OPUSMeasurement will start and stop Macros according to the
    current value of StateInterface: measurements_should_be_running."""
    def __init__(self, initial_config: types.Config):
        self.config = initial_config
        self.initialized = False
        self.current_experiment = self.config.opus.experiment_path.root
        if self.config.general.test_mode or (sys.platform != "win32"):
            return

        self.__initialize()

    def __initialize(self) -> None:
        """Initialize the DDE connection and sets up the conversaton."""

        assert sys.platform == "win32"

        # Force close all OPUS instances that are running to prevent
        # Pyra opening multiple instances of OPUS
        # if self.opus_application_running():
        #     logger.debug("Force-closing OPUS")
        #     processes = [p.name() for p in psutil.process_iter()]
        #     opus_processes = list(
        #         filter(
        #             lambda p: ("opus.exe" in p.lower()) or ("opuscore.exe" in p.lower()),
        #             processes,
        #         )
        #     )
        #     logger.debug(f"Found {len(opus_processes)} OPUS processes: {opus_processes}")
        #     try:
        #         for p in opus_processes:
        #             exit_code = os.system(f"taskkill /f /im {p}")
        #             assert (
        #                 exit_code == 0
        #             ), f'taskkill  of "{p}" ended with an exit_code of {exit_code}'
        #             logger.debug(f'Successfully closed OPUS instance "{p}"')
        #     except Exception as e:
        #         logger.warning(f"Failed to close OPUS: {e}")

        # note: dde servers talk to dde servers
        self.server = _dde.CreateServer()
        self.server.Create("Client")
        self.conversation = _dde.CreateConversation(self.server)
        self.last_cycle_automation_status = 0
        self.initialized = True

    def run(self, new_config: types.Config) -> None:
        """Called in every cycle of the main loop. Starts and
        stops OPUS.exe based on the present sun angle. Reads
        StateInterface: measurements_should_be_running and starts
        and stops the OPUS macro."""

        # loads latest config
        self.config = new_config
        if self.config.general.test_mode or (sys.platform != "win32"):
            logger.debug(
                "Skipping OpusMeasurement in test mode and on non-windows systems"
            )
            return

        logger.info("Running OpusMeasurement")
        logger.debug("Updating JSON Config Variables")

        # check for PYRA Test Mode status
        # everything afterwards will be skipped if PYRA Test Mode is active
        if self.config.general.test_mode:
            logger.info("Test mode active.")
            return

        if not self.initialized:
            self.__initialize()

        # start or stops opus.exe depending on sun angle
        self.automated_process_handling()

        # check and reload experiment if updated in config.json
        self.check_for_experiment_change()

        # checks IP connection to FTIR spectrometer
        if self.__is_em27_responsive():
            logger.debug("Successful ping to EM27.")
        else:
            logger.info("EM27 seems to be disconnected.")

        # check for automation state flank changes
        measurements_should_be_running = (
            interfaces.StateInterface.read().measurements_should_be_running
        )
        if self.last_cycle_automation_status != measurements_should_be_running:
            if measurements_should_be_running:
                # flank change 0 -> 1: start macro
                logger.info("Starting OPUS Macro.")
                self.start_macro()
            else:
                # flank change 1 -> 0: stop macro
                logger.info("Stopping OPUS Macro.")
                self.stop_macro()

        # save the automation status for the next run
        self.last_cycle_automation_status = measurements_should_be_running

    def __connect_to_dde_opus(self) -> None:
        """Connects to the OPUS server over DDE."""
        assert sys.platform == "win32"
        try:
            self.conversation.ConnectTo("OPUS", "OPUS/System")
            logger.info("Connected to OPUS DDE Server.")
        except:
            logger.info("Could not connect to OPUS DDE Server.")

    def __test_dde_connection(self) -> bool:
        """Tests the DDE connection. Tries to reinitialize
        the DDE socket if connection test fails."""

        assert sys.platform == "win32"

        # conversation.Connected() returns 1 <class 'int'> if connected
        if self.conversation.Connected() == 1:
            return True
        else:
            logger.info("DDE Connection seems to be not working.")
            logger.info("Trying to fix DDE Socket.")
            # destroy socket
            self.__destroy_dde_server()
            # reconnect socket
            self.server = _dde.CreateServer()
            self.server.Create("Client")
            self.conversation = _dde.CreateConversation(self.server)
            self.__connect_to_dde_opus()

            # retest DDE connection
            return self.conversation.Connected() == 1  # type: ignore

    def load_experiment(self) -> None:
        """Loads a new experiment in OPUS over DDE connection."""

        assert sys.platform == "win32"

        self.__connect_to_dde_opus()
        experiment_path = self.config.opus.experiment_path.root

        if not self.__test_dde_connection():
            return
        answer = self.conversation.Request("LOAD_EXPERIMENT " + experiment_path)
        logger.info(f"Loaded new OPUS experiment: {experiment_path}")
        self.current_experiment = experiment_path

    def start_macro(self) -> None:
        """Starts a new macro in OPUS over DDE connection."""
        assert sys.platform == "win32"

        # perform connect
        self.__connect_to_dde_opus()
        if not self.__test_dde_connection():
            return

        # load macro
        macro_path = self.config.opus.macro_path
        answer = self.conversation.Request(f"RUN_MACRO {macro_path}")
        logger.info(f"Started OPUS macro: {macro_path}")

    def stop_macro(self) -> None:
        """Stops the currently running macro in OPUS over DDE
        connection."""

        assert sys.platform == "win32"

        # perform connect
        self.__connect_to_dde_opus()
        if not self.__test_dde_connection():
            return

        # stop macro
        macro_path = os.path.basename(self.config.opus.macro_path.root)
        answer = self.conversation.Request("KILL_MACRO " + macro_path)
        logger.info(f"Stopped OPUS macro: {macro_path}")

    def close_opus(self) -> None:
        """Closes OPUS via DDE call."""

        assert sys.platform == "win32"

        self.__connect_to_dde_opus()

        if not self.__test_dde_connection():
            return
        answer = self.conversation.Request("CLOSE_OPUS")
        logger.info("Stopped OPUS.exe")

    def __shutdown_dde_server(self) -> None:
        """Note the underlying DDE object (ie, Server, Topics
        and Items) are not cleaned up by this call."""

        assert sys.platform == "win32"

        self.server.Shutdown()

    def __destroy_dde_server(self) -> None:
        """Destroys the underlying C++ object."""

        assert sys.platform == "win32"
        self.server.Destroy()

    def __is_em27_responsive(self) -> bool:
        """Pings the EM27 and returns:

        True -> Connected
        False -> Not Connected"""

        assert sys.platform == "win32"

        response = os.system("ping -n 1 " + self.config.opus.em27_ip.root)
        return response == 0

    def start_opus(self) -> None:
        """Starts the OPUS.exe with os.startfile(). This simulates
        a user click on the executable."""

        assert sys.platform == "win32"

        opus_path = self.config.opus.executable_path.root
        opus_username = self.config.opus.username
        opus_password = self.config.opus.password

        # works only > python3.10
        # without cwd CT will have trouble loading its internal database)
        try:
            os.startfile(  # type: ignore
                os.path.basename(opus_path),
                cwd=os.path.dirname(opus_path),
                arguments=f"/LANGUAGE=ENGLISH /DIRECTLOGINPASSWORD={opus_username}@{opus_password}",
                show_cmd=2,
            )
        except AttributeError:
            pass

    def opus_application_running(self) -> bool:
        """Checks if OPUS is already running by identifying the window.

        Returns:
        False if Application is currently not running on OS
        True if Application is currently running on OS
        """
        assert sys.platform == "win32"

        # FindWindow(className, windowName)
        # className: String, The window class name to find, else None
        # windowName: String, The window name (ie,title) to find, else None
        opus_username = self.config.opus.username
        opus_windows_name = (
            f"OPUS - Operator: {opus_username}  (Administrator) - [Display - default.ows]"
        )
        try:
            if _win32ui.FindWindow(
                None,
                opus_windows_name,
            ):
                return True
            return False
        except _win32ui.error:
            return False

    def sun_angle_is_too_low(self) -> bool:
        """Checks defined sun angle in config. Closes OPUS at
        the end of the day to start up fresh the next day."""

        assert sys.platform == "win32"

        return (
            utils.Astronomy.get_current_sun_elevation(self.config)
            < self.config.general.min_sun_elevation
        )

    def automated_process_handling(self) -> None:
        """Start OPUS.exe if not running and sun angle conditions
        satisfied. Shuts down OPUS.exe if running and sun angle
        conditions not satisfied."""

        assert sys.platform == "win32"

        if self.sun_angle_is_too_low():
            # Close OPUS if running
            if self.opus_application_running():
                logger.debug("Requesting OPUS night shutdown.")
                # CLOSE_OPUS needs all macros closed to work. stop_macro() is
                # called just in case
                self.stop_macro()
                time.sleep(5)
                self.close_opus()

        else:
            # start OPUS if not currently running
            if not self.opus_application_running():
                logger.info("Start OPUS.")
                self.start_opus()
                self.wait_for_opus_startup()
                logger.info("Loading OPUS Experiment.")
                self.load_experiment()
                # returns to give OPUS time to start until next call of run()
                return

    def wait_for_opus_startup(self) -> None:
        """Checks for OPUS to be running. Breaks out of the loop
        after a defined time."""

        assert sys.platform == "win32"

        start_time = time.time()
        while True:
            # brakes when OPUS is up and running
            if self.opus_application_running():
                break
            time.sleep(0.5)

            # breaks after 60s of waiting
            if time.time() - start_time > 60:
                break

    def check_for_experiment_change(self) -> None:
        """Compares the experiment in the config with the current
        active experiment. To reload an experiment during an active
        macro the macro needs to be stopped first."""

        assert sys.platform == "win32"

        if self.config.opus.experiment_path.root != self.current_experiment:
            if interfaces.StateInterface.read_persistent(
            ).active_opus_macro_id == -1:
                self.load_experiment()
            else:
                self.stop_macro()
                time.sleep(5)
                self.load_experiment()
                time.sleep(5)
                self.start_macro()

    def test_setup(self) -> None:
        """Function to test the functonality of this module. Starts
        up OPUS, loads an experiment, starts a macro and stops it
        after 10s."""

        assert sys.platform == "win32"

        opus_is_running = self.opus_application_running()
        if not opus_is_running:
            self.start_opus()
            try_count = 0
            while try_count < 10:
                if self.opus_application_running():
                    break
                try_count += 1
                time.sleep(6)

        assert self.opus_application_running()
        assert self.__test_dde_connection()

        self.load_experiment()
        time.sleep(2)

        self.start_macro()
        time.sleep(10)

        self.stop_macro()
