import datetime
import threading
import time
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils

logger = utils.Logger(origin="measurement-decision")


class MeasurementDecisionThread(AbstractThread):
    """Thread for checking the system's state (CPU usage, disk utilization, etc.)"""
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=MeasurementDecisionThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        # TODO: implement #232

        while True:
            try:
                t1 = time.time()

                logger.info("Loading configuration file")
                config = types.Config.load()

                logger.info("Loading state file")
                state = interfaces.StateInterface.load_state()

                # FETCH COORDINATES AND SUN ELEVATION

                camtracker_coordinates = utils.Astronomy.get_camtracker_coordinates(config)
                logger.debug(
                    f"Coordinates used from CamTracker (lat, lon, alt): {camtracker_coordinates}."
                )
                sun_elevation = utils.Astronomy.get_current_sun_elevation(
                    config,
                    lat=camtracker_coordinates[0],
                    lon=camtracker_coordinates[1],
                    alt=camtracker_coordinates[2],
                )
                logger.debug(f"Theoretical sun elevation is: {sun_elevation} degrees.")

                # DECIDING WHETHER TO MEASURE

                d = config.measurement_decision
                logger.debug(f"Decision mode for measurements is: {d.mode}.")

                measurements_should_be_running: bool
                if state.plc_state.state.rain == True:
                    logger.debug("not trying to measuring when PLC detected rain")
                    measurements_should_be_running = False
                else:
                    if d.mode == "manual":
                        measurements_should_be_running = d.manual_decision_result
                    elif d.mode == "cli":
                        measurements_should_be_running = d.cli_decision_result
                    else:
                        measurements_should_be_running = MeasurementDecisionThread.get_automatic_decision(
                            config, state, sun_elevation
                        )

                logger.info(
                    f"Measurements should be running is set to: {measurements_should_be_running}."
                )

                # UPDATE STATE

                interfaces.ActivityHistoryInterface.add_datapoint(
                    cli_calls=state.recent_cli_calls,
                    is_measuring=measurements_should_be_running,
                    is_uploading=state.upload_is_running,
                )
                with interfaces.StateInterface.update_state() as s:
                    s.position.latitude = camtracker_coordinates[0]
                    s.position.longitude = camtracker_coordinates[1]
                    s.position.altitude = camtracker_coordinates[2]
                    s.position.sun_elevation = sun_elevation
                    s.measurements_should_be_running = measurements_should_be_running
                    s.recent_cli_calls -= state.recent_cli_calls
                    state.exceptions_state.clear_exception_origin("measurement-decision")

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, 60 - (t2 - t1))
                logger.info(f"Sleeping {sleep_time} seconds")
                time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.add_exception(origin="measurement-decision", exception=e)

    @staticmethod
    def get_automatic_decision(
        config: types.Config,
        state: types.StateObject,
        current_sun_elevation: float,
    ) -> bool:
        """Evaluates the activated automatic mode triggers (Sun Angle,
        Time, Helios). Reads the config to consider activated measurement
        triggers. Evaluates active measurement triggers and combines their
        states by logical conjunction."""

        logger.debug("Evaluating automatic decision")

        triggers = config.measurement_triggers
        if config.helios is None:
            if triggers.consider_helios:
                logger.warning("Helios is not configured, but is set as a trigger.")
            triggers.consider_helios = False

        # If not triggers are considered during automatic mode return False
        if not any([
            triggers.consider_sun_elevation,
            triggers.consider_time,
            triggers.consider_helios,
        ]):
            logger.info("No triggers are activated.")
            return False

        # Evaluate sun elevation if trigger is active
        if triggers.consider_sun_elevation:
            logger.info("Sun elevation as a trigger is considered.")
            if config.general.min_sun_elevation > triggers.min_sun_elevation:
                logger.warning(
                    "`config.general.min_sun_elevation` is higher than `config.measurement_triggers.min_sun_elevation`. This might be a mistake."
                )
            min_sun_elevation = max(config.general.min_sun_elevation, triggers.min_sun_elevation)
            if current_sun_elevation > min_sun_elevation:
                logger.debug("Sun angle is above threshold.")
            else:
                logger.debug("Sun angle is below threshold.")
                return False

        # Evaluate time if trigger is active
        if triggers.consider_time:
            logger.info("Time as a trigger is considered.")
            time_is_valid = (
                triggers.start_time.as_datetime_time() < datetime.datetime.now().time() <
                triggers.stop_time.as_datetime_time()
            )
            logger.debug(f"Time conditions are {'' if time_is_valid else 'not '}fulfilled.")
            if not time_is_valid:
                return False

        # Read latest Helios decision from StateInterface if trigger is active
        # Helios runs in a thread and evaluates the sun conditions consistanly during day.
        if triggers.consider_helios:
            logger.info("Helios as a trigger is considered.")
            helios_result = state.helios_indicates_good_conditions

            if helios_result == "inconclusive" or helios_result is None:
                logger.debug(f"Helios does not nave enough images yet.")
                return False

            logger.debug(
                f"Helios indicates {'good' if helios_result == 'yes' else 'bad'} sun conditions."
            )
            return helios_result == "yes"

        return True