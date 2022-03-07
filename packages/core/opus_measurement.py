# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)

# TODO: Mock the behaviour of OPUS when testing
# TODO: Write parameters like marco/experiment target in JSON file
# TODO: Read parameters from JSON file


import logging
import win32ui
import dde

logger = logging.getLogger("pyra.core")


class OpusMeasurement:
    """Creates a working DDE connection to the OPUS DDE Server.
    Allows to remotely control experiments and macros in OPUS over the established DDE
    connection.
    """
    def __init__(self):
        #note: dde servers talk to dde servers
        self.server = dde.CreateServer()
        self.server.Create("Client")
        self.conversation = dde.CreateConversation(self.server)


    @staticmethod
    def run():
        logger.info("Running OpusMeasurement")
        pass

    def connect_to_dde_opus(self):
        try:
            self.conversation.ConnectTo("OPUS", "OPUS/System")
            logger.info("Connected to OPUS DDE Server.")
        except:
            logger.info("Could not connect to OPUS DDE Server.")

    def test_dde_connection(self):
        """Tests the DDE connection.
        Tries to reinitialize the DDE socket if connection test fails.
         """

        #conversation.Connected() returns 1 <class 'int'> if connected
        if self.conversation.Connected() == 1:
            return True
        else:
            logger.info("DDE Connection seems to be not working.")
            logger.info("Trying to fix DDE Socket.")
            #destroy socket
            self.destroy_dde_server()
            #reconnect socket
            self.server = dde.CreateServer()
            self.server.Create("Client")
            self.conversation = dde.CreateConversation(self.server)
            self.connect_to_dde_opus()

            #retest DDE connection
            if self.conversation.Connected() == 1:
                return True
            else:
                return False


    def load_experiment(self, target):
        """Loads a new experiment in OPUS over DDE connection.
        """
        self.connect_to_dde_opus()

        if self.test_dde_connection():
            answer = self.conversation.Request("LOAD_EXPERIMENT " + target)

            if 'OK' in answer:
                logger.info("Loaded new OPUS experiment: {}.".format(target))
            else:
                logger.info("Could not load OPUS experiment as expected.")

    def start_macro(self, target):
        """Starts a new macro in OPUS over DDE connection.
        """
        self.connect_to_dde_opus()

        if self.test_dde_connection():
            answer = self.conversation.Request("RUN_MACRO " + target)

            if 'OK' in answer:
                logger.info("Started OPUS macro: {}.".format(target))
            else:
                logger.info("Could not start OPUS macro as expected.")

    def stop_macro(self, target):
        """Stops the currently running macro in OPUS over DDE connection.
        """
        self.connect_to_dde_opus()

        if self.test_dde_connection():
            answer = self.conversation.Request("KILL_MACRO " + target)

            if 'OK' in answer:
                logger.info("Stopped OPUS macro: {}.".format(target))
            else:
                logger.info("Could not stop OPUS macro as expected.")

    def shutdown_dde_server(self):
        """Note the underlying DDE object (ie, Server, Topics and Items) are not cleaned up by this call.
        """
        self.server.Shutdown()

    def destroy_dde_server(self):
        """Destroys the underlying C++ object.
        """
        self.server.Destroy()