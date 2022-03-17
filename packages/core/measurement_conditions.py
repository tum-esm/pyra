# Measurement conditions checks for start and stop conditions that are set in
# the parameters json file. It can check for environmental conditions like sun
# status, temporal conditions like current time, or manual user input.

# TODO: Integrate VBDSD sun status



import logging

logger = logging.getLogger("pyra.core")


class MeasurementConditions:
    @staticmethod
    def run():
        logger.info("Running MeasurementConditions")
        pass
