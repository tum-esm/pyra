import threading
import time
from typing import Optional

import tum_esm_utils

from packages.core import interfaces, types, utils

from ..abstract_thread import AbstractThread


class AEMETEnclosureThread(AbstractThread):
    """Thread interacting with the AEMET Enclosure"""

    logger_origin = "aemet-enclosure-thread"

    @staticmethod
    def should_be_running(config: types.Config, logger: utils.Logger) -> bool:
        """Based on the config, should the thread be running or not?"""

        return config.aemet_enclosure is not None

    @staticmethod
    def get_new_thread_object(logs_lock: threading.Lock) -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(
            target=AEMETEnclosureThread.main,
            daemon=True,
            args=(logs_lock,),
        )

    @staticmethod
    def main(logs_lock: threading.Lock, headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="aemet-enclosure", lock=logs_lock, just_print=headless)
        logger.info("Starting AEMET Enclosure thread")

        enclosure_interface: Optional[interfaces.AEMETEnclosureInterface] = None

        exception_was_set: Optional[bool] = None
        thread_start_time = time.time()

        state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
            filepath=interfaces.state_interface.STATE_LOCK_PATH,
            timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
            poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
        )

        try:
            while True:
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
                enclosure_config = config.aemet_enclosure
                if enclosure_config is None:
                    logger.info("AEMET Enclosure configuration not found, shutting down")
                    break

                if config.general.test_mode:
                    logger.info("AEMET Enclosure thread is skipped in test mode")
                    time.sleep(15)
                    continue

                # SETTING UP INTERFACE

                if enclosure_interface is None:
                    logger.debug("Setting up enclosure interface")
                    enclosure_interface = interfaces.AEMETEnclosureInterface(
                        config=enclosure_config,
                        state_lock=state_lock,
                        logger=logger,
                    )
                else:
                    enclosure_interface.update_config(new_config=enclosure_config)

                # UPDATING RECONNECTION STATE

                try:
                    # READING DATALOGGER STATE

                    logger.debug("Reading datalogger state")
                    enclosure_interface.read(immediate_write_to_central_state=False)

                    logger.debug("Updating enclosure state")
                    with interfaces.StateInterface.update_state(state_lock, logger) as s:
                        s.aemet_enclosure_state = enclosure_interface.state

                    logger.debug("Logging enclosure state")
                    utils.AEMETEnclosureLogger.log(config, s)

                    logger.info(
                        f"Enclosure is running on datalogger software version {enclosure_interface.state.datalogger_software_version}"
                    )

                    # ENCLOSURE SPECIFIC LOGIC

                    if enclosure_config.controlled_by_user:
                        logger.debug("Enclosure is controlled by user, skipping control logic")
                    else:
                        # If auto mode is not 0, set it to 0 (manual mode)
                        if enclosure_interface.state.auto_mode != 0:
                            logger.debug("Auto mode is not 0, setting it to 0")
                            enclosure_interface.set_enclosure_mode("manual")

                        # Set enhanced security mode to 1 if it's not already 1
                        if enclosure_interface.state.enhanced_security_mode != 1:
                            logger.debug("Enhanced security mode is not 1, setting it to 1")
                            enclosure_interface.set_enhanced_security_mode(True)

                        # Load the current state
                        state = interfaces.StateInterface.load_state(state_lock, logger)

                        # If toggle spectrometer power is enabled, toggle spectrometer power if night
                        if enclosure_config.use_em27_power_plug:
                            if state.position.sun_elevation is None:
                                logger.warning(
                                    "Sun elevation is not yet set, skipping spectrometer power toggle"
                                )
                            else:
                                min_sun_angle = config.general.min_sun_elevation - 3
                                power_should_be_on = state.position.sun_elevation > min_sun_angle

                                if power_should_be_on and (
                                    not enclosure_interface.state.em27_has_power
                                ):
                                    logger.info("Powering up the spectrometer")
                                    enclosure_interface.set_em27_power(True)

                                elif (not power_should_be_on) and (
                                    enclosure_interface.state.em27_has_power
                                ):
                                    logger.info("Powering down the spectrometer")
                                    enclosure_interface.set_em27_power(False)

                        # only control the cover if the enclosure did no open or close it for safety reasons
                        skip_cover_control: bool = False

                        # If closed due to weather conditions, don't do anything else
                        # If opened due to high internal humidity, don't do anything else
                        if enclosure_interface.state.closed_due_to_rain:
                            logger.info("Enclosure is closed due to rain, skipping cover control")
                            skip_cover_control = True
                        elif enclosure_interface.state.closed_due_to_wind_velocity:
                            logger.info(
                                "Enclosure is closed due to high wind speed, skipping cover control"
                            )
                            skip_cover_control = True
                        elif enclosure_interface.state.closed_due_to_internal_air_temperature:
                            logger.info(
                                "Enclosure is closed due to high internal air temperature, skipping cover control"
                            )
                            skip_cover_control = True
                        elif enclosure_interface.state.closed_due_to_external_air_temperature:
                            logger.info(
                                "Enclosure is closed due to low external air temperature, skipping cover control"
                            )
                            skip_cover_control = True
                        elif enclosure_interface.state.closed_due_to_internal_relative_humidity:
                            logger.info(
                                "Enclosure is closed due to high internal relative humidity, skipping cover control"
                            )
                            skip_cover_control = True
                        elif enclosure_interface.state.closed_due_to_external_relative_humidity:
                            logger.info(
                                "Enclosure is closed due to high external relative humidity, skipping cover control"
                            )
                            skip_cover_control = True
                        elif enclosure_interface.state.opened_due_to_elevated_internal_humidity:
                            logger.info(
                                "Enclosure is opened due to high internal relative humidity, skipping cover control"
                            )
                            skip_cover_control = True

                        # If alert level is 2, don't do anything else
                        if enclosure_interface.state.alert_level == 2:
                            logger.info("Enclosure is in alert level 2, skipping cover control")
                            skip_cover_control = True

                        if not skip_cover_control:
                            logger.debug("Cover is managed by Pyra")

                            if state.measurements_should_be_running is None:
                                logger.warning(
                                    "Measurements should be running is not yet set, skipping cover control"
                                )
                            else:
                                if state.measurements_should_be_running and (
                                    enclosure_interface.state.pretty_cover_status != "open"
                                ):
                                    logger.info(
                                        "Measurements should be running but cover is not open, opening cover"
                                    )
                                    enclosure_interface.open_cover()

                                if (not state.measurements_should_be_running) and (
                                    enclosure_interface.state.pretty_cover_status != "closed"
                                ):
                                    logger.info(
                                        "Measurements should not be running but cover is not closed, closing cover"
                                    )
                                    enclosure_interface.close_cover()

                    # `exception_was_set` variable used to recude the number of state updates
                    if not exception_was_set:
                        exception_was_set = False
                        with interfaces.StateInterface.update_state(state_lock, logger) as s:
                            s.exceptions_state.clear_exception_origin(origin="aemet-enclosure")

                    # SLEEP

                    t2 = time.time()
                    sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                    logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)

                except interfaces.AEMETEnclosureInterface.DataloggerError as e:
                    logger.error("Datalogger connection lost during interaction")
                    logger.exception(e)
                    enclosure_interface = None
                    logger.info("Waiting 60 seconds before retrying")
                    time.sleep(60)
                    continue

        except Exception as e:
            logger.exception(e)
            with interfaces.StateInterface.update_state(state_lock, logger) as s:
                s.exceptions_state.add_exception(origin="aemet-enclosure", exception=e)
