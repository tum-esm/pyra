# ==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220421
# version           : 1.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.
# ==============================================================================

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)

# TODO: Add option for OPUS MockServer usage


import os
import time

# the following imports should be provided by pywin32
try:
    import pywin32
    import win32con
    import win32process
    import win32ui
    import dde

    windows_libraries_available = True
except ModuleNotFoundError:
    windows_libraries_available = False

from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.opus-measurement")


class OpusMeasurement:
    """Creates a working DDE connection to the OPUS DDE Server.
    Allows to remotely control experiments and macros in OPUS over the
    established DDE connection.
    """

    def __init__(self, initial_setup: dict, initial_parameters: dict):
        self._SETUP = initial_setup
        self._PARAMS = initial_parameters
        if not windows_libraries_available:
            logger.info("Windows libraries not available, class is inactive")
            return

        # note: dde servers talk to dde servers
        self.server = dde.CreateServer()
        self.server.Create("Client")
        self.conversation = dde.CreateConversation(self.server)
        self.last_cycle_automation_status = 0

    def run(self, new_setup: dict, new_parameters: dict):
        self._SETUP, self._PARAMS = new_setup, new_parameters

        if not windows_libraries_available:
            return

        logger.info("Running OpusMeasurement")
        logger.debug("Updating JSON Config Variables")

        # check for PYRA Test Mode status
        # everything afterwards will be skipped if PYRA Test Mode is active
        if self._PARAMS["pyra"]["test_mode"] == 1:
            logger.info("Test mode active.")
            return

        # start OPUS if not currently running
        if not self.__opus_application_running:
            self.__start_opus()
            logger.info("Start OPUS.")
            # returns to give OPUS time to start until next call of run()
            return

        # check for automation state flank changes
        if (
            self.last_cycle_automation_status
            != self._PARAMS["pyra"]["automation_status"]
        ):
            if self._PARAMS["pyra"]["automation_status"] == 1:
                # flank change 0 -> 1: load experiment, start macro
                self.__load_experiment()
                logger.info("Load OPUS Experiment.")
                time.sleep(1)
                self.__start_macro()
                logger.info("Start OPUS Macro.")

            if self._PARAMS["pyra"]["automation_status"] == 0:
                # flank change 1 -> 0: stop macro
                self.__stop_macro()
                logger.info("Stop OPUS Macro.")

        # save the automation status for the next run
        self.last_cycle_automation_status = self._PARAMS["pyra"]["automation_status"]

        if self.__is_em27_connected:
            logger.info("Successful ping to EM27.")
        else:
            logger.info("EM27 seems to be not connected.")

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

    def __load_experiment(self, full_path):
        """Loads a new experiment in OPUS over DDE connection."""
        self.__connect_to_dde_opus()

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("LOAD_EXPERIMENT " + full_path)

        if "OK" in answer:
            logger.info("Loaded new OPUS experiment: {}.".format(full_path))
        else:
            logger.info("Could not load OPUS experiment as expected.")

    def __start_macro(self, full_path):
        """Starts a new macro in OPUS over DDE connection."""
        self.__connect_to_dde_opus()

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("RUN_MACRO " + full_path)

        if "OK" in answer:
            logger.info("Started OPUS macro: {}.".format(full_path))
        else:
            logger.info("Could not start OPUS macro as expected.")

    def __stop_macro(self, full_path):
        """Stops the currently running macro in OPUS over DDE connection."""
        self.__connect_to_dde_opus()

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

    @property
    def __is_em27_connected(self):
        """Pings the EM27 and returns:

        True -> Connected
        False -> Not Connected"""
        response = os.system("ping -n 1" + self._SETUP["em27"]["ip"])

        if response == 0:
            return True
        else:
            return False

    def __start_opus(self):
        """Uses win32process frm pywin32 module to start up OPUS
        Returns pywin32 process information for later usage.
        """
        # http://timgolden.me.uk/pywin32-docs/win32process.html
        opus_call = self._SETUP["opus"]["executable_full_path"]
        hProcess, hThread, dwProcessId, dwThreadId = pywin32.CreateProcess(
            None,
            opus_call,
            None,
            None,
            0,
            win32con.NORMAL_PRIORITY_CLASS,
            None,
            None,
            win32process.STARTUPINFO(),
        )

        # return (hProcess, hThread, dwProcessId, dwThreadId)

    @property
    def __opus_application_running(self):
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
