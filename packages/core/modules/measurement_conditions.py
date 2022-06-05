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
# Measurement conditions checks for start and stop conditions that are set in
# the parameters json file. It can check for environmental conditions like sun
# status, temporal conditions like current time, or manual user input.
# ==============================================================================

import datetime
from packages.core.utils import StateInterface, Astronomy, Logger

logger = Logger(origin="pyra.core.measurement-conditions")


def get_times_from_tuples(_triggers: any):
    now = datetime.datetime.now()
    current_time = datetime.time(now.hour, now.minute, now.second)
    start_time = datetime.time(*_triggers["start_time"])
    end_time = datetime.time(*_triggers["stop_time"])
    return current_time, start_time, end_time


class MeasurementConditions:
    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config

    def run(self, new_config: dict):
        self._CONFIG = new_config
        _triggers = self._CONFIG["measurement_triggers"]
        logger.info("Running MeasurementConditions")
        automation_should_be_running = True

        # TODO: Use new logic that replaces "manually_enforced"

        # the "manually_enforced" option (when set to true) makes
        # the decision process ignore all other factors
        if not _triggers["manually_enforced"]:

            # consider sun elevation
            if _triggers["consider_sun_elevation"]:
                current_sun_elevation = Astronomy.get_current_sun_elevation()
                sun_is_too_low = current_sun_elevation < _triggers["min_sun_elevation"]
                sun_is_too_high = current_sun_elevation > _triggers["max_sun_elevation"]
                if sun_is_too_low or sun_is_too_high:
                    automation_should_be_running &= False

            # consider daytime
            if _triggers["consider_time"]:
                current_time, start_time, end_time = get_times_from_tuples(_triggers)
                time_is_too_early = current_time < start_time
                time_is_too_late = current_time > end_time
                if time_is_too_early or time_is_too_late:
                    automation_should_be_running &= False

            # consider evaluation from the VBDSD
            if _triggers["consider_vbdsd"] and (self._CONFIG["vbdsd"] is not None):
                # Don't consider VBDSD if it does not have enough
                # images yet, which will result in a state of "None"
                if StateInterface.read()["vbdsd_indicates_good_conditions"] == False:
                    automation_should_be_running &= False

        StateInterface.update(
            {"automation_should_be_running": automation_should_be_running}
        )
