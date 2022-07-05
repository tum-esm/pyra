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
from packages.core.utils import Astronomy, StateInterface, Logger, OSInterface

logger = Logger(origin="measurement-conditions")


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

        # TODO: Move system state checks into their own module

        # check os system stability
        ans = OSInterface.check_cpu_usage()
        logger.debug("Current CPU usage for all cores is {}%.".format(ans))

        ans = OSInterface.check_average_system_load()
        logger.info(
            "The average system load in the past 1/5/15 minutes was" " {}.".format(ans)
        )

        ans = OSInterface.check_memory_usage()
        logger.debug("Current v_memory usage for the system is {}.".format(ans))

        ans = OSInterface.time_since_os_boot()
        logger.debug("The system is running since {}.".format(ans))

        ans = OSInterface.check_disk_space()
        logger.debug("The disk is currently filled with {}%.".format(ans))

        # raises error if disk_space is below 10%
        OSInterface.validate_disk_space()
        # raises error if system battery is below 20%
        OSInterface.validate_system_battery()

        decision = self._CONFIG["measurement_decision"]
        triggers = self._CONFIG["measurement_triggers"]

        if decision["mode"] == "manual":
            logger.debug("Decision mode for measurements is: Manual.")
            automation_should_be_running = decision["manual_decision_result"]

        if decision["mode"] == "cli":
            logger.debug("Decision mode for measurements is: CLI.")
            automation_should_be_running = decision["cli_decision_result"]

        if decision["mode"] == "automatic":
            logger.debug("Decision mode for measurements is: Automatic.")
            if (
                triggers["consider_sun_elevation"]
                or triggers["consider_time"]
                or (triggers["consider_vbdsd"] and (self._CONFIG["vbdsd"] is not None))
            ):
                # Will be set to be false below if at least one trigger decides to
                automation_should_be_running = True
            else:
                automation_should_be_running = False

            # consider sun elevation
            if triggers["consider_sun_elevation"]:
                logger.info("Sun elevation as a trigger is evaluated.")
                current_sun_elevation = Astronomy.get_current_sun_elevation()
                sun_above_threshold = (
                    current_sun_elevation > triggers["min_sun_elevation"] * Astronomy.units.deg
                )
                # TODO: remove max_sun_elevation as not needed
                if sun_above_threshold:
                    logger.debug("Sun angle is above threshold.")

                if not sun_above_threshold:
                    logger.debug("Sun angle is below threshold.")
                    automation_should_be_running &= False

            # consider daytime
            if triggers["consider_time"]:
                logger.info("Time as a trigger is considered.")
                current_time, start_time, end_time = get_times_from_tuples(triggers)
                if current_time > start_time and current_time < end_time:
                    logger.debug("Time conditions are fulfilled.")
                if current_time < start_time or current_time > end_time:
                    logger.debug("Time conditions are not fulfilled.")
                    automation_should_be_running &= False

            # consider evaluation from the VBDSD
            if triggers["consider_vbdsd"] and (self._CONFIG["vbdsd"] is not None):
                logger.info("VBDSD as a trigger is considered.")
                # Don't consider VBDSD if it does not have enough
                # images yet, which will result in a state of "None"
                if StateInterface.read()["vbdsd_indicates_good_conditions"] == True:
                    logger.debug("VBDSD indicates good sun conditions.")
                if StateInterface.read()["vbdsd_indicates_good_conditions"] == False:
                    logger.debug("VBDSD indicates bad sun conditions.")
                    automation_should_be_running &= False

        logger.info(
            "Measurements should be running is set to: {}.".format(
                automation_should_be_running
            )
        )
        StateInterface.update({"automation_should_be_running": automation_should_be_running})
