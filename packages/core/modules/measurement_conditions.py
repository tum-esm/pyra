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
import astropy.units as astropy_units
from packages.core.utils import Astronomy, StateInterface, Logger, OSInfo

logger = Logger(origin="pyra.core.measurement-conditions")


def get_times_from_tuples(triggers: any):
    now = datetime.datetime.now()
    current_time = datetime.time(now.hour, now.minute, now.second)
    start_time = datetime.time(*triggers["start_time"])
    end_time = datetime.time(*triggers["stop_time"])
    return current_time, start_time, end_time


class MeasurementConditions:
    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config

        if self._CONFIG["general"]["test_mode"]:
            return

    def run(self, new_config: dict):
        self._CONFIG = new_config
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping MeasurementConditions in test mode")
            return

        logger.info("Running MeasurementConditions")

        # check os system stability
        ans = OSInfo.check_cpu_usage()
        logger.debug("Current CPU usage for all cores is {}%.".format(ans))

        ans = OSInfo.check_average_system_load()
        logger.info(
            "The average system load in the past 1/5/15 minutes was" " {}.".format(ans)
        )

        ans = OSInfo.check_memory_usage()
        logger.debug("Current v_memory usage for the system is {}.".format(ans))

        ans = OSInfo.time_since_os_boot()
        logger.debug("The system is running since {}.".format(ans))

        ans = OSInfo.check_disk_space()
        logger.debug("The disk is currently filled with {}%.".format(ans))

        # raises error if disk_space is below 10%
        OSInfo.validate_disk_space()
        # raises error if system battery is below 20%
        OSInfo.validate_system_battery()

        #TODO: Move measurement_decision to state.json and reset it with core start
        decision = self._CONFIG["measurement_decision"]
        triggers = self._CONFIG["measurement_triggers"]

        if decision["mode"] == "manual":
            automation_should_be_running = decision["manual_decision_result"]

        if decision["mode"] == "cli":
            automation_should_be_running = decision["cli_decision_result"]

        if decision["mode"] == "automatic":
            automation_should_be_running = True

            # consider sun elevation
            if triggers["consider_sun_elevation"]:
                current_sun_elevation = Astronomy.get_current_sun_elevation()
                sun_is_too_low = current_sun_elevation < triggers["min_sun_elevation"] * astropy_units.deg
                sun_is_too_high = current_sun_elevation > triggers["max_sun_elevation"] * astropy_units.deg
                if sun_is_too_low or sun_is_too_high:
                    automation_should_be_running &= False

            # consider daytime
            if triggers["consider_time"]:
                current_time, start_time, end_time = get_times_from_tuples(triggers)
                time_is_too_early = current_time < start_time
                time_is_too_late = current_time > end_time
                if time_is_too_early or time_is_too_late:
                    automation_should_be_running &= False

            # consider evaluation from the VBDSD
            if triggers["consider_vbdsd"] and (self._CONFIG["vbdsd"] is not None):
                # Don't consider VBDSD if it does not have enough
                # images yet, which will result in a state of "None"
                if StateInterface.read()["vbdsd_indicates_good_conditions"] == False:
                    automation_should_be_running &= False

        StateInterface.update(
            {"automation_should_be_running": automation_should_be_running}
        )
