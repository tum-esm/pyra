import datetime
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="measurement-conditions")


def is_time_trigger_active(
    config: types.ConfigDict,
) -> bool:
    """Returns true if time triggers in the config specify
    that it should be measured right now"""
    now = datetime.datetime.now()
    current_time = datetime.time(now.hour, now.minute, now.second)
    start_time = datetime.time(**config["measurement_triggers"]["start_time"])
    end_time = datetime.time(**config["measurement_triggers"]["stop_time"])
    return (current_time > start_time) and (current_time < end_time)


class MeasurementConditions:
    """MeasurementConditions allows operation in three different modes:
    Manual, Automatic, Manual, and CLI. Whenever a decision is made the
    parameter measurements_should_be_running in StateInterface is updated.

    In Manual mode, the user has full control over whether measurements
    should be active. The user-controlled state can be controlled by the
    Pyra UI.

    In Automatic mode, three different triggers are considered: Sun
    Elevation, Time, and Helios State. These triggers may also be active
    in any combination at the same time. Measurements are only set to be
    running if all triggers agree, while measurements will be set to be
    not active if at least one of the active triggers decides to stop
    measurements.

    In CLI mode, triggers from external sources can be considered. This
    option is available for custom-built systems or sensors not part of
    Pyra 4. It is also possible in this mode to move the measurement
    control to remote systems i.e. by SSH."""

    def __init__(self, initial_config: types.ConfigDict) -> None:
        self._CONFIG = initial_config

    def run(self, new_config: types.ConfigDict) -> None:
        """Called in every cycle of the main loop.
        Updates StateInterface: measurements_should_be_running based on the selected mode, triggers
        and present conditions."""

        self._CONFIG = new_config

        # Skip rest of the function if test mode is active
        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping MeasurementConditions in test mode")
            return

        logger.info("Running MeasurementConditions")
        decision = self._CONFIG["measurement_decision"]
        logger.debug(f"Decision mode for measurements is: {decision['mode']}.")

        # Selection and evaluation of the current set measurement mode
        if decision["mode"] == "manual":
            measurements_should_be_running = decision["manual_decision_result"]
        if decision["mode"] == "cli":
            measurements_should_be_running = decision["cli_decision_result"]
        if decision["mode"] == "automatic":
            measurements_should_be_running = self._get_automatic_decision()

        if (
            interfaces.StateInterface.read()["measurements_should_be_running"]
            != measurements_should_be_running
        ):
            utils.Logger.log_activity_event(
                "start-measurements" if measurements_should_be_running else "stop-measurements"
            )

        logger.info(
            f"Measurements should be running is set to: {measurements_should_be_running}."
        )
        # Update of the StateInterface with the latest measurement decision
        interfaces.StateInterface.update(
            {"measurements_should_be_running": measurements_should_be_running}
        )

    def _get_automatic_decision(self) -> bool:
        """Evaluates the activated automatic mode triggers (Sun Angle, Time, Helios).
        Reads the config to consider activated measurement triggers. Evaluates active measurement
        triggers and combines their states by logical conjunction.
        """
        triggers = self._CONFIG["measurement_triggers"]
        if self._CONFIG["helios"] is None:
            triggers["consider_helios"] = False

        # If not triggers are considered during automatic mode return False
        if not any(
            [
                triggers["consider_sun_elevation"],
                triggers["consider_time"],
                triggers["consider_helios"],
            ]
        ):
            return False

        # Evaluate sun elevation if trigger is active
        if triggers["consider_sun_elevation"]:
            logger.info("Sun elevation as a trigger is considered.")
            current_sun_elevation = utils.Astronomy.get_current_sun_elevation(self._CONFIG)
            min_sun_elevation = max(
                self._CONFIG["general"]["min_sun_elevation"], triggers["min_sun_elevation"]
            )
            if current_sun_elevation > min_sun_elevation:
                logger.debug("Sun angle is above threshold.")
            else:
                logger.debug("Sun angle is below threshold.")
                return False

        # Evaluate time if trigger is active
        if triggers["consider_time"]:
            logger.info("Time as a trigger is considered.")
            time_is_valid = is_time_trigger_active(self._CONFIG)
            logger.debug(f"Time conditions are {'' if time_is_valid else 'not '}fulfilled.")
            if not time_is_valid:
                return False

        # Read latest Helios decision from StateInterface if trigger is active
        # Helios runs in a thread and evaluates the sun conditions consistanly during day.
        if triggers["consider_helios"]:
            logger.info("Helios as a trigger is considered.")
            helios_result = interfaces.StateInterface.read()[
                "helios_indicates_good_conditions"
            ]

            if helios_result is None:
                logger.debug(f"Helios does not nave enough images yet.")
                return False

            logger.debug(
                f"Helios indicates {'good' if helios_result else 'bad'} sun conditions."
            )
            return helios_result

        return True
