import datetime
import threading
import time
from typing import Optional

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


class TUMEnclosureThread(AbstractThread):
    """Thread for to evaluate whether to conduct measurements or not.

    CAS = Condition Assessment System."""

    logger_origin = "tum-enclosure-thread"

    @staticmethod
    def should_be_running(config: types.Config, logger: utils.Logger) -> bool:
        """Based on the config, should the thread be running or not?"""

        return config.tum_enclosure is not None

    @staticmethod
    def get_new_thread_object(logs_lock: threading.Lock) -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(
            target=TUMEnclosureThread.main,
            daemon=True,
            args=(logs_lock,),
        )

    @staticmethod
    def main(logs_lock: threading.Lock, headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="tum-enclosure", lock=logs_lock)
        logger.info("Starting TUM Enclosure thread")

        plc_interface: Optional[interfaces.TUMEnclosureInterface] = None
        last_plc_connection_time: float = time.time()
        last_camera_down_time: Optional[float] = None
        exception_was_set: Optional[bool] = None
        thread_start_time = time.time()

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
                enclosure_config = config.tum_enclosure
                if enclosure_config is None:
                    logger.info("TUM Enclosure configuration not found, shutting down")
                    break

                if config.general.test_mode:
                    logger.info("TUM Enclosure thread is skipped in test mode")
                    time.sleep(15)
                    continue

                # CONNECTING TO PLC

                if plc_interface is None:
                    logger.debug("Connecting to PLC")
                    plc_interface = interfaces.TUMEnclosureInterface(
                        plc_version=enclosure_config.version,
                        plc_ip=enclosure_config.ip,
                        logger=logger,
                    )
                    try:
                        plc_interface.connect()
                        plc_interface.set_auto_temperature(True)
                        logger.info("Successfully connected to PLC")
                    except interfaces.TUMEnclosureInterface.PLCError as e:
                        logger.error("Could not connect to PLC")
                        logger.exception(e)
                        plc_interface = None
                        if last_plc_connection_time < (time.time() - 360):
                            exception_was_set = True
                            with interfaces.StateInterface.update_state(logger) as s:
                                s.exceptions_state.add_exception_state_item(
                                    types.ExceptionStateItem(
                                        origin="tum-enclosure",
                                        subject="Could not connect to PLC for 6 minutes",
                                    )
                                )
                        logger.info("Waiting 60 seconds before retrying")
                        time.sleep(60)
                        continue
                else:
                    plc_interface.update_config(
                        new_plc_version=enclosure_config.version,
                        new_plc_ip=enclosure_config.ip,
                    )
                    if not plc_interface.is_connected():
                        logger.error("PLC connection lost")
                        plc_interface = None
                        logger.info("Waiting 60 seconds before retrying")
                        time.sleep(60)
                        continue

                # UPDATING RECONNECTION STATE

                # now the PLC is connected - otherwise it would loop in the section above
                last_plc_connection_time = time.time()
                try:
                    # READING PLC

                    logger.debug("Reading PLC registers")
                    plc_state = plc_interface.read()

                    logger.debug("Updating enclosure state")
                    with interfaces.StateInterface.update_state(logger) as s:
                        s.tum_enclosure_state = plc_state

                    logger.debug("Logging enclosure state")
                    utils.TUMEnclosureLogger.log(config, s)

                    # CHECKING FOR OPEN COVER DURING RAIN

                    if plc_state.state.rain:
                        if plc_state.actors.current_angle != 0:
                            time.sleep(15)
                            if plc_interface.get_cover_angle() != 0:
                                logger.warning("Rain detected, but cover is closed yet")
                                exception_was_set = True
                                with interfaces.StateInterface.update_state(logger) as s:
                                    s.exceptions_state.add_exception_state_item(
                                        types.ExceptionStateItem(
                                            origin="tum-enclosure",
                                            subject="Rain detected but cover is not closed",
                                        )
                                    )
                        logger.debug("Skipping remaining PLC logic during rain")
                        if not exception_was_set:
                            exception_was_set = False
                            with interfaces.StateInterface.update_state(logger) as s:
                                s.exceptions_state.clear_exception_origin(origin="tum-enclosure")
                        continue

                    # SKIP REMAINING LOGIC IF IN USER CONTROLLED MODE

                    if enclosure_config.controlled_by_user:
                        logger.info(
                            "User is controlling the TUM Enclosure, skipping operational logic"
                        )
                        if not exception_was_set:
                            exception_was_set = False
                            with interfaces.StateInterface.update_state(logger) as s:
                                s.exceptions_state.clear_exception_origin(origin="tum-enclosure")
                        t2 = time.time()
                        sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                        logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                        time.sleep(sleep_time)
                        continue

                    # RESETTING PLC

                    TUMEnclosureThread.clear_plc_reset(plc_interface, logger)

                    # CAMERA POWER CYCLE

                    # power up the camera if it is off but should be on
                    if (last_camera_down_time is None) and (not plc_state.power.camera):
                        logger.info("Powering up the camera as it is off but should be on")
                        plc_interface.set_power_camera(True)
                        plc_state.power.camera = True

                    current_time = datetime.datetime.now()

                    # power down the camera
                    if (
                        (current_time.hour == 0)
                        and (current_time.minute < 5)
                        and (last_camera_down_time is None)
                    ):
                        logger.info("Powering down the camera")
                        plc_interface.set_power_camera(False)
                        plc_state.power.camera = False
                        last_camera_down_time = time.time()

                    # power up the camera
                    if (last_camera_down_time is not None) and (
                        (time.time() - last_camera_down_time) > 300
                    ):
                        logger.info("Powering up the camera")
                        plc_interface.set_power_camera(True)
                        plc_state.power.camera = True
                        last_camera_down_time = None

                    # SPECTROMETER POWER

                    state = interfaces.StateInterface.load_state(logger)

                    if state.position.sun_elevation is None:
                        logger.warning(
                            "Sun elevation is not yet set, skipping spectrometer power toggle"
                        )
                    else:
                        min_sun_angle = config.general.min_sun_elevation - 3
                        power_should_be_on = state.position.sun_elevation > min_sun_angle

                        if power_should_be_on and (not plc_state.power.spectrometer):
                            logger.info("Powering up the spectrometer")
                            plc_interface.set_power_spectrometer(True)
                            plc_state.power.spectrometer = True

                        elif (not power_should_be_on) and (plc_state.power.spectrometer):
                            logger.info("Powering down the spectrometer")
                            plc_interface.set_power_spectrometer(False)
                            plc_state.power.spectrometer = False

                    # SYNC COVER TO TRACKER

                    if state.measurements_should_be_running is None:
                        logger.warning(
                            "Measurements should be running is not yet set, skipping cover sync"
                        )
                    else:
                        # open cover
                        if state.measurements_should_be_running and (
                            not plc_state.control.sync_to_tracker
                        ):
                            logger.info("Syncing cover to tracker")
                            plc_interface.set_sync_to_tracker(True)
                            plc_state.control.sync_to_tracker = True

                        # close cover
                        elif (not state.measurements_should_be_running) and (
                            plc_state.control.sync_to_tracker
                        ):
                            logger.info("Disabling syncing cover to tracker")
                            plc_interface.set_sync_to_tracker(False)
                            plc_state.control.sync_to_tracker = False

                        # check if cover is closed
                        if not plc_state.control.sync_to_tracker:
                            if plc_state.actors.current_angle != 0:
                                logger.info("Manually setting cover angle to 0")
                                plc_interface.set_manual_control(True)
                                plc_interface.set_cover_angle(0)
                                plc_interface.set_manual_control(False)
                                start_time = time.time()

                                while True:
                                    TUMEnclosureThread.clear_plc_reset(
                                        plc_interface, logger, timeout=30
                                    )
                                    time.sleep(5)
                                    if plc_interface.get_cover_angle() == 0:
                                        plc_state.actors.current_angle = 0
                                        logger.info("Cover is closed now")
                                        break

                                    if (time.time() - start_time) > 62:
                                        logger.error("Cover is still not closed")
                                        exception_was_set = True
                                        with interfaces.StateInterface.update_state(logger) as s:
                                            s.exceptions_state.add_exception_state_item(
                                                types.ExceptionStateItem(
                                                    origin="tum-enclosure",
                                                    subject="Cover did not closed after disabling sync to tracker and moving to 0°",
                                                )
                                            )
                                        break

                    # CLEAR EXCEPTIONS

                    # `exception_was_set` variable used to recude the number of state updates
                    if not exception_was_set:
                        exception_was_set = False
                        with interfaces.StateInterface.update_state(logger) as s:
                            s.exceptions_state.clear_exception_origin(origin="tum-enclosure")

                    # SLEEP

                    t2 = time.time()
                    sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                    logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)

                except interfaces.TUMEnclosureInterface.PLCError as e:
                    logger.error("PLC connection lost during interaction")
                    logger.exception(e)
                    plc_interface = None
                    logger.info("Waiting 60 seconds before retrying")
                    time.sleep(60)
                    continue

        except Exception as e:
            logger.exception(e)
            with interfaces.StateInterface.update_state(logger) as s:
                s.exceptions_state.add_exception(origin="tum-enclosure", exception=e)

    @staticmethod
    def clear_plc_reset(
        plc_interface: interfaces.TUMEnclosureInterface,
        logger: utils.Logger,
        timeout: int = 180,
    ) -> None:
        """Resetting the PLC if needed. If the reset doesn't work,
        add an exception to the state object."""

        r = plc_interface.reset_is_needed()
        m = plc_interface.motor_has_failed()

        if r or m:
            if plc_interface.rain_is_detected():
                logger.info("Rain is detected, skipping PLC reset")
                return

            if r:
                logger.info("PLC indicates a reset is needed")
            if m:
                logger.info("PLC indicates that the motor has failed")
            logger.info(f"Trying to reset for {timeout} second until raising exception")
            start_time = time.time()
            while True:
                logger.info("sending reset")
                plc_interface.reset()
                time.sleep(5)
                r = plc_interface.reset_is_needed()
                m = plc_interface.motor_has_failed()
                if not (r or m):
                    logger.info("PLC reset was successful")
                    break

                if (time.time() - start_time) > timeout:
                    with interfaces.StateInterface.update_state(logger) as s:
                        s.exceptions_state.add_exception_state_item(
                            types.ExceptionStateItem(
                                origin="tum-enclosure",
                                subject="PLC reset was required but did not work",
                            )
                        )
                    break
        else:
            logger.debug("PLC reset is not needed")
            with interfaces.StateInterface.update_state(logger) as s:
                s.exceptions_state.clear_exception_subject(
                    subject="PLC reset was required but did not work"
                )

    @staticmethod
    def force_cover_close(config: types.Config, logger: utils.Logger) -> None:
        """Force the cover to close by disabling syncing to tracker."""

        enclosure_config = config.tum_enclosure
        if enclosure_config is None:
            logger.error("TUM Enclosure configuration not found")
            return

        plc_interface = interfaces.TUMEnclosureInterface(
            plc_version=enclosure_config.version,
            plc_ip=enclosure_config.ip,
            logger=logger,
        )
        logger.info("Connecting to PLC")
        plc_interface.connect()
        plc_interface.set_auto_temperature(True)
        TUMEnclosureThread.clear_plc_reset(plc_interface, logger)

        logger.info("Manually closing cover")
        plc_interface.set_sync_to_tracker(False)
        plc_interface.set_manual_control(True)
        plc_interface.set_cover_angle(0)
        plc_interface.set_manual_control(False)

        logger.info("Disconnecting from PLC")
        plc_interface.disconnect()
