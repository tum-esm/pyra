# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)

# TODO: Add option for OPUS MockServer usage


import logging
from msilib.schema import Property

import win32ui
import dde

logger = logging.getLogger("pyra.core")


class OpusMeasurement:
    """Creates a working DDE connection to the OPUS DDE Server.
    Allows to remotely control experiments and macros in OPUS over the
    established DDE connection.
    """

    def __init__(self):
        # note: dde servers talk to dde servers
        self.server = dde.CreateServer()
        self.server.Create("Client")
        self.conversation = dde.CreateConversation(self.server)
        self._PARAMS = {}
        self._SETUP = {}

    def run(self, setup: dict, params: dict):
        logger.info("Running OpusMeasurement")
        logger.debug("Updating JSON Config Variables")
        self.__update_json_config(setup, params)

        # check for PYRA Test Mode status
        if self._PARAMS["PYRA_test_mode"] == 1:
            logger.info("Test mode active.")
            return
        # everything afterwards will be skipped if PYRA Test Mode is active

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

    def __update_json_config(self, setup: dict, params: dict):
        self._SETUP = setup
        self._PARAMS = params

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
        """Loads a new experiment in OPUS over DDE connection.
        """
        self.__connect_to_dde_opus()

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("LOAD_EXPERIMENT " + full_path)

        if 'OK' in answer:
            logger.info("Loaded new OPUS experiment: {}.".format(full_path))
        else:
            logger.info("Could not load OPUS experiment as expected.")

    def __start_macro(self, full_path):
        """Starts a new macro in OPUS over DDE connection.
        """
        self.__connect_to_dde_opus()

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("RUN_MACRO " + full_path)

        if 'OK' in answer:
            logger.info("Started OPUS macro: {}.".format(full_path))
        else:
            logger.info("Could not start OPUS macro as expected.")

    def __stop_macro(self, full_path):
        """Stops the currently running macro in OPUS over DDE connection.
        """
        self.__connect_to_dde_opus()

        if not self.__test_dde_connection:
            return
        answer = self.conversation.Request("KILL_MACRO " + full_path)

        if 'OK' in answer:
            logger.info("Stopped OPUS macro: {}.".format(full_path))
        else:
            logger.info("Could not stop OPUS macro as expected.")

    def __shutdown_dde_server(self):
        """Note the underlying DDE object (ie, Server, Topics and Items) are
        not cleaned up by this call.
        """
        self.server.Shutdown()

    def __destroy_dde_server(self):
        """Destroys the underlying C++ object.
        """
        self.server.Destroy()

    @Property
    def __is_em27_connected(self):
        """Pings the EM27 and returns:

        True -> Connected
        False -> Not Connected"""
        # TODO: Implement function
        # use try if module give exceptions
        return False
