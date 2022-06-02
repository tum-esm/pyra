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
from packages.core.utils.astronomy import Astronomy
from packages.core.utils.json_file_interaction import State
from packages.core.utils.logger import Logger
from packages.core.utils.os_info import OSInfo

logger = Logger(origin="pyra.core.measurement-conditions")


def current_time_is_before_noon() -> bool:
    return datetime.datetime.now().hour < 13


# returns (hour, minute, second) tuple
def current_time_is_in_range_tuples(t_start: tuple[int], t_end: tuple[int]):
    now = datetime.datetime.now()
    current_time = datetime.time(now.hour, now.minute, now.second)
    start_time = datetime.time(*t_start)
    end_time = datetime.time(*t_end)
    return current_time > start_time and current_time < end_time


class MeasurementConditions:
    def __init__(self, initial_setup: dict, initial_parameters: dict):
        self._SETUP = initial_setup
        self._PARAMS = initial_parameters

    def run(self, new_setup: dict, new_parameters: dict):
        self._SETUP, self._PARAMS = new_setup, new_parameters
        _triggers = self._PARAMS["measurement_triggers"]

        logger.info("Running MeasurementConditions")

        #check os system stability
        ans = OSInfo.check_cpu_usage()
        logger.debug("Current CPU usage for all cores is {}%.".format(ans))

        ans = OSInfo.check_average_system_load()
        logger.info("The average system load in the past 1/5/15 minutes was"
                     " {}.".format(ans))

        ans = OSInfo.check_memory_usage()
        logger.debug("Current v_memory usage for the system is {}.".format(ans))

        ans = OSInfo.time_since_os_boot()
        logger.debug("The system is running since {}.".format(ans))

        ans = OSInfo.check_disk_space()
        logger.debug("The disk is currently filled with {}%.".format(ans))

        #raises error if disk_space is below 10%
        OSInfo.validate_disk_space()
        #raises error if system battery is below 20%
        OSInfo.validate_system_battery()

        # TODO: add cli enforced option?
        #check for conditions to start measurements
        automation_should_be_running = True

        # the "manually_enforced" option (when set to true) makes
        # the decision process ignore all other factors
        if not _triggers["manually_enforced"]:

            # consider elevation on mornings and evenings
            if _triggers["type"]["sun_angle"]:
                min_required_elevation = (
                    _triggers["sun_angle_start"]
                    if current_time_is_before_noon()
                    else _triggers["sun_angle_stop"]
                )
                if Astronomy.get_current_sun_elevation() < min_required_elevation:
                    automation_should_be_running &= False

            # consider start_time and end_time
            if _triggers["type"]["time"]:
                if not current_time_is_in_range_tuples(
                    _triggers["start_time"], _triggers["stop_time"]
                ):
                    automation_should_be_running &= False

            # consider evaluation from the vbdsd
            if _triggers["type"]["vbdsd"]:
                # Don't consider VBDSD if it does not have enough
                # images yet, which will result in a state of "None"
                if State.read()["vbdsd_indicates_good_conditions"] == False:
                    automation_should_be_running &= False

        State.update({"automation_should_be_running": automation_should_be_running})
