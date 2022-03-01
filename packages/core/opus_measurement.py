# OPUS is the measurement software for the spectrometer EM27/Sun. It is used to
# start and stop measurements and define measurement or saving parameters.

# TODO: Implement this for our version of OPUS

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any version of OPUS (for later updates)

# TODO: Mock the behaviour of OPUS when testing


import logging

logger = logging.getLogger("pyra.core")


class OpusMeasurement:
    @staticmethod
    def run():
        logger.info("Running OpusMeasurement")
        pass
