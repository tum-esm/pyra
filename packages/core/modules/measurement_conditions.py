import datetime
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="measurement-conditions")


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
    def __init__(self, initial_config: types.Config) -> None:
        self.config = initial_config

    def run(self, new_config: types.Config) -> None:
        """Called in every cycle of the main loop. Updates the state
        based on the selected mode, triggers and present conditions."""

        self.config = new_config
        current_state = interfaces.StateInterface.load_state()

        # Fetch and log current sun elevation
        camtracker_coordinates = utils.Astronomy.get_camtracker_coordinates(
            self.config
        )
        logger.debug(
            f"Coordinates used from CamTracker (lat, lon, alt): {camtracker_coordinates}."
        )
        sun_elevation = utils.Astronomy.get_current_sun_elevation(
            self.config,
            lat=camtracker_coordinates[0],
            lon=camtracker_coordinates[1],
            alt=camtracker_coordinates[2],
        )
        logger.debug(f"Theoretical sun elevation is: {sun_elevation} degrees.")

        # Skip rest of the function if test mode is active
        if self.config.general.test_mode:
            interfaces.ActivityHistoryInterface.add_datapoint(
                cli_calls=current_state.recent_cli_calls
            )
            with interfaces.StateInterface.update_state_in_context() as state:
                state.position.latitude = camtracker_coordinates[0]
                state.position.longitude = camtracker_coordinates[1]
                state.position.altitude = camtracker_coordinates[2]
                state.position.sun_elevation = sun_elevation
                state.recent_cli_calls -= current_state.recent_cli_calls
            logger.debug("Skipping MeasurementConditions in test mode")
            return

        logger.info("Running MeasurementConditions")
        decision = self.config.measurement_decision
        logger.debug(f"Decision mode for measurements is: {decision.mode}.")

        # Selection and evaluation of the current set measurement mode
        measurements_should_be_running: bool
        if decision.mode == "manual":
            measurements_should_be_running = decision.manual_decision_result
        elif decision.mode == "cli":
            measurements_should_be_running = decision.cli_decision_result
        else:
            measurements_should_be_running = self._get_automatic_decision(
                current_state
            )

        logger.info(
            f"Measurements should be running is set to: {measurements_should_be_running}."
        )
        interfaces.ActivityHistoryInterface.add_datapoint(
            cli_calls=current_state.recent_cli_calls,
            is_measuring=measurements_should_be_running
        )
        with interfaces.StateInterface.update_state_in_context() as state:
            state.position.latitude = camtracker_coordinates[0]
            state.position.longitude = camtracker_coordinates[1]
            state.position.altitude = camtracker_coordinates[2]
            state.position.sun_elevation = sun_elevation
            state.measurements_should_be_running = measurements_should_be_running
            state.recent_cli_calls -= current_state.recent_cli_calls

    def _get_automatic_decision(self, current_state: types.StateObject) -> bool:
        """Evaluates the activated automatic mode triggers (Sun Angle,
        Time, Helios). Reads the config to consider activated measurement
        triggers. Evaluates active measurement triggers and combines their
        states by logical conjunction."""

        triggers = self.config.measurement_triggers
        if self.config.helios is None:
            triggers.consider_helios = False

        # If not triggers are considered during automatic mode return False
        if not any([
            triggers.consider_sun_elevation,
            triggers.consider_time,
            triggers.consider_helios,
        ]):
            return False

        # Evaluate sun elevation if trigger is active
        if triggers.consider_sun_elevation:
            logger.info("Sun elevation as a trigger is considered.")
            current_sun_elevation = utils.Astronomy.get_current_sun_elevation(
                self.config
            )
            min_sun_elevation = max(
                self.config.general.min_sun_elevation,
                triggers.min_sun_elevation
            )
            if current_sun_elevation > min_sun_elevation:
                logger.debug("Sun angle is above threshold.")
            else:
                logger.debug("Sun angle is below threshold.")
                return False

        # Evaluate time if trigger is active
        if triggers.consider_time:
            logger.info("Time as a trigger is considered.")
            current_time = datetime.datetime.now().time()
            time_is_valid = (
                self.config.measurement_triggers.start_time.as_datetime_time() <
                current_time <
                self.config.measurement_triggers.stop_time.as_datetime_time()
            )
            logger.debug(
                f"Time conditions are {'' if time_is_valid else 'not '}fulfilled."
            )
            if not time_is_valid:
                return False

        # Read latest Helios decision from StateInterface if trigger is active
        # Helios runs in a thread and evaluates the sun conditions consistanly during day.
        if triggers.consider_helios:
            logger.info("Helios as a trigger is considered.")
            helios_result = current_state.helios_indicates_good_conditions

            if helios_result == "inconclusive" or helios_result is None:
                logger.debug(f"Helios does not nave enough images yet.")
                return False

            logger.debug(
                f"Helios indicates {'good' if helios_result == 'yes' else 'bad'} sun conditions."
            )
            return helios_result == "yes"

        return True
