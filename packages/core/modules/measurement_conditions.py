import datetime
from packages.core.utils import Astronomy, StateInterface, Logger, types

logger = Logger(origin="measurement-conditions")


# TODO: add type annotation
def is_time_trigger_active(
    config: types.ConfigDict,
) -> bool:
    now = datetime.datetime.now()
    current_time = datetime.time(now.hour, now.minute, now.second)
    start_time = datetime.time(**config["measurement_triggers"]["start_time"])
    end_time = datetime.time(**config["measurement_triggers"]["stop_time"])
    return (current_time > start_time) and (current_time < end_time)


class MeasurementConditions:
    def __init__(self, initial_config: types.ConfigDict) -> None:
        self._CONFIG = initial_config

    def run(self, new_config: types.ConfigDict) -> None:
        self._CONFIG = new_config
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping MeasurementConditions in test mode")
            return

        logger.info("Running MeasurementConditions")
        decision = self._CONFIG["measurement_decision"]
        logger.debug(f"Decision mode for measurements is: {decision['mode']}.")

        if decision["mode"] == "manual":
            measurements_should_be_running = decision["manual_decision_result"]
        if decision["mode"] == "cli":
            measurements_should_be_running = decision["cli_decision_result"]
        if decision["mode"] == "automatic":
            measurements_should_be_running = self._get_automatic_decision()

        if (
            StateInterface.read()["measurements_should_be_running"]
            != measurements_should_be_running
        ):
            Logger.log_activity_event(
                "start-measurements" if measurements_should_be_running else "stop-measurements"
            )

        logger.info(
            f"Measurements should be running is set to: {measurements_should_be_running}."
        )
        StateInterface.update(
            {"measurements_should_be_running": measurements_should_be_running}
        )

    def _get_automatic_decision(self) -> bool:
        triggers = self._CONFIG["measurement_triggers"]
        if self._CONFIG["helios"] is None:
            triggers["consider_helios"] = False

        if not any(
            [
                triggers["consider_sun_elevation"],
                triggers["consider_time"],
                triggers["consider_helios"],
            ]
        ):
            return False

        if triggers["consider_sun_elevation"]:
            logger.info("Sun elevation as a trigger is considered.")
            current_sun_elevation = Astronomy.get_current_sun_elevation()
            min_sun_elevation = max(
                self._CONFIG["general"]["min_sun_elevation"], triggers["min_sun_elevation"]
            )
            sun_above_threshold = current_sun_elevation > (
                min_sun_elevation * Astronomy.units.deg
            )
            if sun_above_threshold:
                logger.debug("Sun angle is above threshold.")
            else:
                logger.debug("Sun angle is below threshold.")
                return False

        if triggers["consider_time"]:
            logger.info("Time as a trigger is considered.")
            time_is_valid = is_time_trigger_active(self._CONFIG)
            logger.debug(f"Time conditions are {'' if time_is_valid else 'not '}fulfilled.")
            if not time_is_valid:
                return False

        if triggers["consider_helios"]:
            logger.info("Helios as a trigger is considered.")
            helios_result = StateInterface.read()["helios_indicates_good_conditions"]

            if helios_result is None:
                logger.debug(f"Helios does not nave enough images yet.")
                return False

            logger.debug(
                f"Helios indicates {'good' if helios_result else 'bad'} sun conditions."
            )
            return helios_result

        return True
