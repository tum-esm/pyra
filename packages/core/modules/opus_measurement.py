import os
import sys
import time
from packages.core.utils import Logger, StateInterface, Astronomy


# these imports are provided by pywin32
if sys.platform == "win32":
    import win32con  # type: ignore
    import win32process  # type: ignore
    import win32ui  # type: ignore
    import dde  # type: ignore


logger = Logger(origin="opus-measurement")


class SpectrometerError(Exception):
    pass


class OpusMeasurement:
    """Creates a working DDE connection to the OPUS DDE Server.
    Allows to remotely control experiments and macros in OPUS over the
    established DDE connection.
    """

    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config
        self.initialized = False
        self.current_experiment = None
        if self._CONFIG["general"]["test_mode"]:
            return

        self._initialize()

    def _initialize(self):
        # note: dde servers talk to dde servers
        self.server = dde.CreateServer()
        self.server.Create("Client")
        self.conversation = dde.CreateConversation(self.server)
        self.last_cycle_automation_status = 0
        self.initialized = True

    def run(self, new_config: dict):
        self._CONFIG = new_config
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping OpusMeasurement in test mode")
            return

        logger.info("Running OpusMeasurement")
        logger.debug("Updating JSON Config Variables")

        # check for PYRA Test Mode status
        # everything afterwards will be skipped if PYRA Test Mode is active
        if self._CONFIG["general"]["test_mode"]:
            logger.info("Test mode active.")
            return

        if not self.initialized:
            self._initialize()

        # start or stops opus.exe depending on sun angle
        self.automated_process_handling()

        # check and reload experiment if updated in config.json
        self.check_for_experiment_change()

        if self.__is_em27_responsive:
            logger.debug("Successful ping to EM27.")
        else:
            logger.info("EM27 seems to be disconnected.")

        # check for automation state flank changes
        measurements_should_be_running = StateInterface.read()[
            "measurements_should_be_running"
        ]
        if self.last_cycle_automation_status != measurements_should_be_running:
            if measurements_should_be_running:
                # flank change 0 -> 1: load experiment, start macro
                logger.info("Starting OPUS Macro.")
                self.start_macro()
            else:
                # flank change 1 -> 0: stop macro
                logger.info("Stopping OPUS Macro.")
                self.stop_macro()

        # save the automation status for the next run
        self.last_cycle_automation_status = measurements_should_be_running

    def __connect_to_dde_opus(self):
        try:
            self.conversation.ConnectTo("OPUS", "OPUS/System")
            logger.info("Connected to OPUS DDE Server.")
        except:
            logger.info("Could not connect to OPUS DDE Server.")

    @property
    def __test_dde_connection(self):
        """Tests the DDE connection.
        Tries to reinitialize the DDE socket if connection test fails.
        """

        # conversation.Connected() returns 1 <class 'int'> if connected
        if self.conversation.Connected() == 1:
            return True
        else:
            logger.info("DDE Connection seems to be not working.")
            logger.info("Trying to fix DDE Socket.")
            # destroy socket
            self.__destroy_dde_server()
            # reconnect socket
            self.server = dde.CreateServer()
            self.server.Create("Client")
            self.conversation = dde.CreateConversation(self.server)
            self.__connect_to_dde_opus()

            # retest DDE connection
            return self.conversation.Connected() == 1

    def load_experiment(self):
        """Loads a new experiment in OPUS over DDE connection."""
        self.__connect_to_dde_opus()
        experiment_path = self._CONFIG["opus"]["experiment_path"]

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("LOAD_EXPERIMENT " + experiment_path)
        logger.info(f"Loaded new OPUS experiment: {experiment_path}")
        self.current_experiment = experiment_path

        # TODO: why does the following logic not work anymore
        """
        if "OK" in answer:
            logger.info("Loaded new OPUS experiment: {}.".format(full_path))
            self.current_experiment = full_path
        else:
            logger.info("Could not load OPUS experiment as expected.")
        """

    def start_macro(self):
        """Starts a new macro in OPUS over DDE connection."""
        self.__connect_to_dde_opus()
        if not self.__test_dde_connection:
            return

        macro_path = self._CONFIG["opus"]["macro_path"]
        answer = self.conversation.Request(f"RUN_MACRO {macro_path}")
        logger.info(f"Started OPUS macro: {macro_path}")

        # TODO: why does the following logic not work anymore
        """
        active_macro_id = str(answer[4:-1])
        StateInterface.update({"active_opus_macro_id": active_macro_id}, persistent=True)

        if "OK" in answer:
            logger.info(f"Started OPUS macro: {macro_basename} with id: {active_macro_id}.")
        else:
            logger.info(f"Could not start OPUS macro with id: {active_macro_id} as expected.")
        """

    def stop_macro(self):
        """Stops the currently running macro in OPUS over DDE connection."""
        self.__connect_to_dde_opus()
        macro_path = os.path.basename(self._CONFIG["opus"]["macro_path"])

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("KILL_MACRO " + macro_path)
        logger.info(f"Stopped OPUS macro: {macro_path}")

        # TODO: why does the following logic not work anymore
        """
        if "OK" in answer:
            logger.info(f"Stopped OPUS macro: {macro_basename} with id: {active_macro_id}.")
            StateInterface.update({"active_opus_macro_id": None}, persistent=True)
        else:
            logger.info(f"Could not stop OPUS macro with id: {active_macro_id} as expected.")
        """

    def close_opus(self):
        """Closes OPUS via DDE."""
        self.__connect_to_dde_opus()

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("CLOSE_OPUS")
        logger.info("Stopped OPUS.exe")

        # TODO: why does the following logic not work anymore
        """
        if "OK" in answer:
            logger.info("Stopped OPUS.exe")
        else:
            logger.info("No response for OPUS.exe close request.")
        """

    def __shutdown_dde_server(self):
        """Note the underlying DDE object (ie, Server, Topics and Items) are
        not cleaned up by this call.
        """
        self.server.Shutdown()

    def __destroy_dde_server(self):
        """Destroys the underlying C++ object."""
        self.server.Destroy()

    def __is_em27_responsive(self):
        """Pings the EM27 and returns:

        True -> Connected
        False -> Not Connected"""
        response = os.system("ping -n 1 " + self._CONFIG["em27"]["ip"])
        return response == 0

    def start_opus(self):
        """Uses os.startfile() to start up OPUS
        This simulates a user click on the opus.exe.
        """

        opus_path = self._CONFIG["opus"]["executable_path"]

        # works only > python3.10
        # without cwd CT will have trouble loading its internal database)
        os.startfile(
            os.path.basename(opus_path),
            cwd=os.path.dirname(opus_path),
            arguments=self._CONFIG["opus"]["executable_parameter"],
            show_cmd=2,
        )

    def opus_application_running(self):
        """Checks if OPUS is already running by identifying the window.

        False if Application is currently not running on OS
        True if Application is currently running on OS
        """
        # FindWindow(className, windowName)
        # className: String, The window class name to find, else None
        # windowName: String, The window name (ie,title) to find, else None
        try:
            if win32ui.FindWindow(
                None,
                "OPUS - Operator: Default  (Administrator) - [Display - default.ows]",
            ):
                return True
        except win32ui.error:
            return False

    def test_setup(self):
        if sys.platform != "win32":
            return

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
        assert self.__test_dde_connection

        self.load_experiment()
        time.sleep(2)

        self.start_macro()
        time.sleep(10)

        self.stop_macro()

    def low_sun_angle_present(self):
        """OPUS closes at the end of the day to start up fresh the next day."""

        # sleep while sun angle is too low
        if Astronomy.get_current_sun_elevation().is_within_bounds(
            None, self._CONFIG["vbdsd"]["min_sun_elevation"] * Astronomy.units.deg
        ):
            return True
        else:
            return False

    def automated_process_handling(self):
        """Start OPUS.exe if not running and sun angle conditions satisfied.
        Shuts down OPUS.exe if running and sun angle conditions not satisfied.
        """

        if not self.low_sun_angle_present():
            # start OPUS if not currently running
            if not self.opus_application_running():
                logger.info("Start OPUS.")
                self.start_opus()
                time.sleep(10)
                logger.info("Loading OPUS Experiment.")
                self.load_experiment()
                # returns to give OPUS time to start until next call of run()
                return
        if self.low_sun_angle_present():
            # Close OPUS if running
            if self.opus_application_running():
                logger.debug("Requesting OPUS night shutdown.")
                # CLOSE_OPUS needs all macros closed to work. stop_macro() is
                # called just in case
                self.stop_macro()
                time.sleep(5)
                self.close_opus()

    def check_for_experiment_change(self):
        """Compares the experiment in the config with the current active experiment.
        To reload an experiment during an active macro the macro needs to be stopped first.
        """

        if self._CONFIG["opus"]["experiment_path"] != self.current_experiment:
            if StateInterface.read(persistent=True)["active_opus_macro_id"] == None:
                self.load_experiment()
            else:
                self.stop_macro()
                time.sleep(5)
                self.load_experiment()
                time.sleep(5)
                self.start_macro()
