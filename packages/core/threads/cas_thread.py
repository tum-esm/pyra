import datetime
import threading
import time

import tum_esm_utils

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


class CASThread(AbstractThread):
    """Thread for to evaluate whether to conduct measurements or not.

    CAS = Condition Assessment System."""

    logger_origin = "cas-thread"

    @staticmethod
    def should_be_running(
        config: types.Config,
        logger: utils.Logger,
    ) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object(
        logs_lock: threading.Lock,
    ) -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(
            target=CASThread.main,
            daemon=True,
            args=(logs_lock,),
        )

    @staticmethod
    def main(
        logs_lock: threading.Lock,
        headless: bool = False,
    ) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="cas", lock=logs_lock)
        logger.info("Starting Condition Assessment System (CAS) thread.")
        last_good_automatic_decision: float = 0
        last_rain_detection: float = 0

        state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
            filepath=interfaces.state_interface.STATE_LOCK_PATH,
            timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
            poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
        )
        thread_start_time = time.time()

        while True:
            try:
                t1 = time.time()
                logger.debug("Starting iteration")

                if (thread_start_time - t1) > 43200:
                    # Windows happens to have a problem with long-running multiprocesses/multithreads
                    logger.debug(
                        "Stopping and restarting thread after 12 hours for stability reasons"
                    )
                    return

                logger.debug("Loading configuration file")
                config = types.Config.load()
                if config.general.test_mode:
                    time.sleep(0.1)  # for the tests to work

                logger.debug("Loading state file")
                state = interfaces.StateInterface.load_state(state_lock, logger)

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

                # RAIN DETECTION

                if state.tum_enclosure_state.state.rain:
                    last_rain_detection = time.time()

                # DECIDING WHETHER TO MEASURE

                d = config.measurement_decision
                logger.info(f"Decision mode for measurements is: {d.mode}.")

                should_measure: bool
                if (time.time() - last_rain_detection) < 180:
                    logger.info(
                        "Not trying to measure when rain was detected within the last 3 minutes."
                    )
                    should_measure = False
                else:
                    if d.mode == "manual":
                        should_measure = d.manual_decision_result
                        if config.general.min_sun_elevation > sun_elevation:
                            logger.debug("Manual decision not considered due to low sun elevation.")
                            should_measure = False
                    elif d.mode == "cli":
                        should_measure = d.cli_decision_result
                    else:
                        should_measure = CASThread.get_automatic_decision(
                            config, logger, state, sun_elevation
                        )
                        if should_measure:
                            last_good_automatic_decision = time.time()
                        else:
                            time_since_last_good_decision = (
                                time.time() - last_good_automatic_decision
                            )
                            if (
                                time_since_last_good_decision
                                < config.measurement_triggers.shutdown_grace_period
                            ):
                                should_measure = True
                                logger.info(
                                    f"Last good automatic decision was {time_since_last_good_decision:.2f} seconds ago. Waiting for {config.measurement_triggers.shutdown_grace_period} seconds of bad conditions until shutting down."
                                )

                logger.info(f"Measurements should be running is set to: {should_measure}.")

                # UPDATE STATE

                with interfaces.StateInterface.update_state(state_lock, logger) as s:
                    s.position.latitude = camtracker_coordinates[0]
                    s.position.longitude = camtracker_coordinates[1]
                    s.position.altitude = camtracker_coordinates[2]
                    s.position.sun_elevation = sun_elevation
                    s.measurements_should_be_running = should_measure
                    s.exceptions_state.clear_exception_origin("cas")

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                with interfaces.StateInterface.update_state(state_lock, logger) as s:
                    s.exceptions_state.add_exception(origin="cas", exception=e)

    @staticmethod
    def get_automatic_decision(
        config: types.Config,
        logger: utils.Logger,
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
        if not any(
            [
                triggers.consider_sun_elevation,
                triggers.consider_time,
                triggers.consider_helios,
            ]
        ):
            logger.warning("No triggers are activated. This might be a mistake.")
            return False

        # Evaluate sun elevation if trigger is active
        if triggers.consider_sun_elevation:
            logger.debug("Sun elevation as a trigger is considered.")
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
            logger.debug("Time as a trigger is considered.")
            time_is_valid = (
                triggers.start_time.as_datetime_time()
                < datetime.datetime.now().time()
                < triggers.stop_time.as_datetime_time()
            )
            logger.debug(f"Time conditions are {'' if time_is_valid else 'not '}fulfilled.")
            if not time_is_valid:
                return False

        # Read latest Helios decision from StateInterface if trigger is active
        # Helios runs in a thread and evaluates the sun conditions consistanly during day.
        if triggers.consider_helios:
            logger.debug("Helios as a trigger is considered.")
            helios_result = state.helios_indicates_good_conditions

            if helios_result == "inconclusive" or helios_result is None:
                logger.debug("Helios does not nave enough images yet.")
                return False

            logger.debug(
                f"Helios indicates {'good' if helios_result == 'yes' else 'bad'} sun conditions."
            )
            return helios_result == "yes"

        return True
