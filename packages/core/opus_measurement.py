# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)

# TODO: Mock the behaviour of OPUS when testing


import logging

logger = logging.getLogger("pyra.core")

# TODO: think of a good class name
class OpusMeasurement:
    @staticmethod
    def run():
        logger.info("Running OpusMeasurement")

        # TODO: Check all conditions, whether to contact OPUS

        # TODO: Send info to OPUS over DDE: 1. location of macro, 2. location of experiment files

        pass
