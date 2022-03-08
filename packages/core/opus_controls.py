# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)

# TODO: Add option for OPUS MockServer usage


import logging

logger = logging.getLogger("pyra.core")

# TODO: Merge Patrick's progress
class OpusControls:
    """Creates a working DDE connection to the OPUS DDE Server.
    Allows to remotely control experiments and macros in OPUS over the established DDE
    connection.
    """

    def run(self, setup: dict, params: dict):
        logger.info("Running OpusControls")

        # TODO: Check all conditions, whether to contact OPUS

        # TODO: Send info to OPUS over DDE: 1. location of macro, 2. location of experiment files

        pass
