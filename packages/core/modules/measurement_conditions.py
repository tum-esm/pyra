import datetime
from packages.core.utils import Astronomy, StateInterface, Logger

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

    def run(self, new_config: dict):
        self._CONFIG = new_config
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping MeasurementConditions in test mode")
            return

        logger.info("Running MeasurementConditions")
        decision = self._CONFIG["measurement_decision"]
        logger.debug(f"Decision mode for measurements is: {decision['mode']}.")

        if decision["mode"] == "manual":
            automation_should_be_running = decision["manual_decision_result"]
        if decision["mode"] == "cli":
            automation_should_be_running = decision["cli_decision_result"]
        if decision["mode"] == "automatic":
            automation_should_be_running = self._get_automatic_decision()

        logger.info(
            f"Measurements should be running is set to: {automation_should_be_running}."
        )
        StateInterface.update({"automation_should_be_running": automation_should_be_running})

    def _get_automatic_decision(self) -> bool:
        triggers = self._CONFIG["measurement_triggers"]
        if self._CONFIG["vbdsd"] is None:
            triggers["consider_vbdsd"] = False

        if not any(
            [
                triggers["consider_sun_elevation"],
                triggers["consider_time"],
                triggers["consider_vbdsd"],
            ]
        ):
            return False

        if triggers["consider_sun_elevation"]:
            logger.info("Sun elevation as a trigger is considered.")
            current_sun_elevation = Astronomy.get_current_sun_elevation()
            sun_above_threshold = (
                current_sun_elevation > triggers["min_sun_elevation"] * Astronomy.units.deg
            )
            # TODO: remove max_sun_elevation as not needed
            if sun_above_threshold:
                logger.debug("Sun angle is above threshold.")

            if not sun_above_threshold:
                logger.debug("Sun angle is below threshold.")
                return False

        if triggers["consider_time"]:
            logger.info("Time as a trigger is considered.")
            current_time, start_time, end_time = get_times_from_tuples(triggers)
            time_is_valid = (current_time > start_time) and (current_time < end_time)
            logger.debug(f"Time conditions are {'' if time_is_valid else 'not '}fulfilled.")
            if not time_is_valid:
                return False

        if triggers["consider_vbdsd"]:
            logger.info("VBDSD as a trigger is considered.")
            vbdsd_result = StateInterface.read()["vbdsd_indicates_good_conditions"]

            if vbdsd_result is None:
                logger.debug(f"VBDSD does not nave enough images yet.")
                return False

            logger.debug(
                f"VBDSD indicates {'good' if vbdsd_result else 'bad'} sun conditions."
            )
            return vbdsd_result

        return True
