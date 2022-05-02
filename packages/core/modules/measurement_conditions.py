# ==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220401
# version           : 3.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# Measurement conditions checks for start and stop conditions that are set in
# the parameters json file. It can check for environmental conditions like sun
# status, temporal conditions like current time, or manual user input.
# ==============================================================================

# TODO: Integrate VBDSD sun status

from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.measurement-conditions")


class MeasurementConditions:
    def __init__(self):
        self._SETUP = {}
        self._PARAMS = {}

    def run(self, new_setup: dict, new_parameters: dict):
        self._SETUP, self._PARAMS = new_setup, new_parameters

        logger.info("Running MeasurementConditions")
        pass

    # allow for multiple options
    # check for time
    # check for sun angle
    # use vbdsd
    # check for user input

    # if self.sun_angle_deg < 10.0 * u.deg: em27 power off
