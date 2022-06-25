# ==============================================================================
# description       :
# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.
# ==============================================================================

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)


import os
import sys
import time
from packages.core.utils import Logger, StateInterface, OSInfo


# these imports are provided by pywin32
if sys.platform == "win32":
    import win32con  # type: ignore
    import win32process  # type: ignore
    import win32ui  # type: ignore
    import dde  # type: ignore


logger = Logger(origin="pyra.core.opus-measurement")


class SpectrometerError(Exception):
    pass


class OpusMeasurement:
    """Creates a working DDE connection to the OPUS DDE Server.
    Allows to remotely control experiments and macros in OPUS over the
    established DDE connection.
    """

    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config
        if self._CONFIG["general"]["test_mode"]:
            return

        # note: dde servers talk to dde servers
        self.server = dde.CreateServer()
        self.server.Create("Client")
        self.conversation = dde.CreateConversation(self.server)
        self.last_cycle_automation_status = 0

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

        # start OPUS if not currently running
        if not self.opus_application_running:
            self.start_opus()
            logger.info("Start OPUS.")
            # returns to give OPUS time to start until next call of run()
            return

        # TODO: fix function OSInfo.check_connection_status
        """
        # check EM27 ip connection
        plc_status = OSInfo.check_connection_status(self._CONFIG["opus"]["em27_ip"])
        logger.debug("The PLC IP connection returned the status {}.".format(plc_status))

        if plc_status == "NO_INFO":
            raise SpectrometerError("Could not find an active EM27 IP connection.")
        """
        if self.__is_em27_responsive:
            logger.info("Successful ping to EM27.")
        else:
            logger.info("EM27 seems to be disconnected.")

        # check for automation state flank changes
        automation_should_be_running = StateInterface.read()[
            "automation_should_be_running"
        ]
        if self.last_cycle_automation_status != automation_should_be_running:
            if automation_should_be_running:
                # flank change 0 -> 1: load experiment, start macro
                logger.info("Loading OPUS Experiment.")
                self.load_experiment()
                time.sleep(1)
                logger.info("Starting OPUS Macro.")
                self.start_macro()
            else:
                # flank change 1 -> 0: stop macro
                logger.info("Stopping OPUS Macro.")
                self.stop_macro()

        # save the automation status for the next run
        self.last_cycle_automation_status = automation_should_be_running

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
            if self.conversation.Connected() == 1:
                return True
            else:
                return False

    def load_experiment(self):
        """Loads a new experiment in OPUS over DDE connection."""
        self.__connect_to_dde_opus()
        full_path = self._CONFIG["opus"]["experiment_path"]

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("LOAD_EXPERIMENT " + full_path)

        if "OK" in answer:
            logger.info("Loaded new OPUS experiment: {}.".format(full_path))
        else:
            logger.info("Could not load OPUS experiment as expected.")

    def start_macro(self):
        """Starts a new macro in OPUS over DDE connection."""
        self.__connect_to_dde_opus()
        full_path = self._CONFIG["opus"]["macro_path"]

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("RUN_MACRO " + full_path)

        if "OK" in answer:
            logger.info("Started OPUS macro: {}.".format(full_path))
        else:
            logger.info("Could not start OPUS macro as expected.")

    def stop_macro(self):
        """Stops the currently running macro in OPUS over DDE connection."""
        self.__connect_to_dde_opus()
        full_path = self._CONFIG["opus"]["macro_path"]

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("KILL_MACRO " + full_path)

        if "OK" in answer:
            logger.info("Stopped OPUS macro: {}.".format(full_path))
        else:
            logger.info("Could not stop OPUS macro as expected.")

    def __shutdown_dde_server(self):
        """Note the underlying DDE object (ie, Server, Topics and Items) are
        not cleaned up by this call.
        """
        self.server.Shutdown()

    def __destroy_dde_server(self):
        """Destroys the underlying C++ object."""
        self.server.Destroy()

    # TODO: is this still needed?
    def __is_em27_responsive(self):
        """Pings the EM27 and returns:

        True -> Connected
        False -> Not Connected"""
        response = os.system("ping -n 1 " + self._SETUP["em27"]["ip"])

        if response == 0:
            return True
        else:
            return False

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


    @property
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

        opus_is_running = self.opus_application_running
        if not opus_is_running:
            self.start_opus()
            try_count = 0
            while try_count < 10:
                if self.opus_application_running:
                    break
                try_count += 1
                time.sleep(6)

        assert self.opus_application_running
        assert self.__test_dde_connection

        print("__is_em27_connected: ", self.__is_em27_responsive)

        self.load_experiment()
        time.sleep(2)

        self.start_macro()
        time.sleep(10)

        self.stop_macro()

        print("__is_em27_connected: ", self.__is_em27_responsive)
