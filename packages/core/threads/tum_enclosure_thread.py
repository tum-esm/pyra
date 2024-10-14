import datetime
import threading
import time
from typing import Optional

import snap7.exceptions
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils

ORIGIN = "tum-enclosure"


class TUMEnclosureThread(AbstractThread):
    """Thread for to evaluate whether to conduct measurements or not.
    
    CAS = Condition Assessment System."""
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return config.tum_enclosure is not None

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=TUMEnclosureThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        logger = utils.Logger(origin=ORIGIN)
        plc_interface: Optional[interfaces.TUMEnclosureInterface] = None
        last_plc_connection_time: Optional[float] = None
        last_camera_down_time: Optional[float] = None
        exception_was_set: Optional[bool] = None

        try:
            while True:
                t1 = time.time()

                logger.info("Loading configuration file")
                config = types.Config.load()

                # CONNECTING TO PLC

                if plc_interface is None:
                    logger.info("Connecting to PLC")
                    plc_interface = interfaces.TUMEnclosureInterface(
                        plc_version=config.tum_enclosure.version,
                        plc_ip=config.tum_enclosure.ip,
                    )
                    try:
                        plc_interface.connect()
                    except snap7.exceptions.Snap7Exception as e:
                        logger.error("Could not connect to PLC")
                        logger.exception(e)
                        plc_interface = None
                        if last_plc_connection_time < (time.time() - 360):
                            exception_was_set = True
                            with interfaces.StateInterface.update_state() as _s:
                                _s.exceptions_state.add_exception_state_item(
                                    types.ExceptionStateItem(
                                        origin=ORIGIN,
                                        subject="Could not connect to PLC for 6 minutes",
                                    )
                                )
                        logger.info("Waiting 60 seconds before retrying")
                        time.sleep(60)
                        continue
                else:
                    plc_interface.update_config(
                        new_plc_version=config.tum_enclosure.version,
                        new_plc_ip=config.tum_enclosure.ip,
                    )
                    if not plc_interface.is_connected():
                        logger.error("PLC connection lost")
                        plc_interface = None
                        logger.info("Waiting 60 seconds before retrying")
                        time.sleep(60)
                        continue

                # UPDATING RECONNECTION STATE

                last_plc_connection_time = time.time()
                if exception_was_set != False:
                    exception_was_set = False
                    with interfaces.StateInterface.update_state() as _s:
                        _s.exceptions_state.clear_exception_subject(
                            subject="Could not connect to PLC for 6 minutes"
                        )

                try:
                    # READING PLC

                    logger.info("Reading PLC registers")
                    plc_state = plc_interface.read()

                    logger.debug("Updating enclosure state")
                    with interfaces.StateInterface.update_state() as s:
                        s.tum_enclosure_state = plc_state

                    logger.debug("Logging enclosure state")
                    utils.TUMEnclosureLogger.log(config, s)

                    # CHECKING FOR OPEN COVER DURING RAIN

                    if plc_state.state.rain and (plc_state.actors.current_angle != 0):
                        time.sleep(5)
                        if plc_interface.get_cover_angle() != 0:
                            logger.warning("Rain detected, but cover is closed yet")

                        # wait 30 seconds for the PLC to close the cover on its own
                        start_time = time.time()
                        while True:
                            if plc_interface.get_cover_angle() == 0:
                                logger.info("Cover is closed now")
                                break

                            if (time.time() - start_time) > 32:
                                logger.warning("Cover is still not closed")
                                exception_was_set = True
                                with interfaces.StateInterface.update_state() as _s:
                                    _s.exceptions_state.add_exception_state_item(
                                        types.ExceptionStateItem(
                                            origin=ORIGIN,
                                            subject="Rain detected but cover is not closed"
                                        )
                                    )
                                break

                            time.sleep(5)

                        if plc_interface.get_cover_angle() != 0:
                            logger.info("Cover is still not closed, trying to close it manually")

                            logger.info("Reading PLC registers")
                            state = plc_interface.read()
                            synced_to_tracker = state.control.sync_to_tracker
                            manual_control = state.control.manual_control
                            while True:
                                TUMEnclosureThread.handle_plc_errors(
                                    plc_interface, logger, timeout=30
                                )

                                if synced_to_tracker != False:
                                    logger.info("Disabling syncing to tracker")
                                    plc_interface.set_sync_to_tracker(False)
                                    synced_to_tracker = False

                                if manual_control != True:
                                    logger.info("Enabling manual control")
                                    plc_interface.set_manual_control(True)
                                    manual_control = True

                                logger.info("Manually setting cover angle to 0")
                                plc_interface.set_cover_angle(0)
                                time.sleep(5)
                                if plc_interface.get_cover_angle() == 0:
                                    logger.info("Cover is closed now")
                                    break

                        continue
                    else:
                        if exception_was_set != False:
                            exception_was_set = False
                            with interfaces.StateInterface.update_state() as _s:
                                _s.exceptions_state.clear_exception_subject(
                                    subject="Rain detected but cover is not closed"
                                )

                    # SKIP REMAINING LOGIC IF IN USER CONTROLLED MODE

                    if config.tum_enclosure.controlled_by_user:
                        logger.info(
                            "User is controlling the TUM Enclosure, skipping operational logic"
                        )
                        t2 = time.time()
                        sleep_time = max(5, 15 - (t2 - t1))
                        logger.info(f"Sleeping {sleep_time} seconds")
                        time.sleep(sleep_time)
                        continue

                    # RESETTING PLC

                    TUMEnclosureThread.handle_plc_errors(plc_interface, logger)

                    # CAMERA POWER CYCLE

                    # power up the camera if it is off but should be on
                    if (last_camera_down_time is None) and (plc_state.power.camera != True):
                        logger.info("Powering up the camera as it is off but should be on")
                        plc_interface.set_power_camera(True)
                        plc_state.power.camera = True

                    current_time = datetime.datetime.now()

                    # power down the camera
                    if ((current_time.hour == 0) and (current_time.minute < 30) and
                        (last_camera_down_time is None)):
                        logger.info("Powering down the camera")
                        plc_interface.set_power_camera(False)
                        plc_state.power.camera = False
                        last_camera_down_time = time.time()

                    # power up the camera
                    if (last_camera_down_time
                        is not None) and ((time.time() - last_camera_down_time) > 300):
                        logger.info("Powering up the camera")
                        plc_interface.set_power_camera(True)
                        plc_state.power.camera = True
                        last_camera_down_time = None

                    # SPECTROMETER POWER

                    state = interfaces.StateInterface.load_state()

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

                        elif (not power_should_be_on) and (plc_state.power.spectrometer == True):
                            logger.info("Powering down the spectrometer")
                            plc_interface.set_power_spectrometer(False)
                            plc_state.power.spectrometer = False

                    # SYNC COVER TO TRACKER

                    # TODO:
                    # wait here until cover is actually closed
                    # if sync to tracker was set, assert that it is still true (no emails though)

                    # CLEAR EXCEPTIONS

                    if exception_was_set != False:
                        exception_was_set = False
                        with interfaces.StateInterface.update_state() as _s:
                            _s.exceptions_state.clear_exception_origin(origin=ORIGIN)

                    # SLEEP

                    t2 = time.time()
                    sleep_time = max(5, 40 - (t2 - t1))
                    logger.info(f"Sleeping {sleep_time} seconds")
                    time.sleep(sleep_time)

                except (
                    snap7.exceptions.Snap7Exception,
                    interfaces.TUMEnclosureInterface.PLCError,
                ) as e:
                    logger.error("PLC connection lost during interaction")
                    logger.exception(e)
                    plc_interface = None
                    logger.info("Waiting 60 seconds before retrying")
                    time.sleep(60)
                    continue

        except Exception as e:
            logger.exception(e)
            with interfaces.StateInterface.update_state() as state:
                state.exceptions_state.add_exception(origin=ORIGIN, exception=e)

    @staticmethod
    def handle_plc_errors(
        plc_interface: interfaces.TUMEnclosureInterface,
        logger: utils.Logger,
        timeout: int = 180
    ) -> None:
        """Resetting the PLC if needed. If the reset doesn't work,
        add an exception to the state object."""

        r = plc_interface.reset_is_needed()
        m = plc_interface.motor_has_failed()
        if r or m:
            if r:
                logger.info("PLC indicates a reset is needed")
            if m:
                logger.info("PLC indicates that the motor has failed")
            start_time = time.time()
            while True:
                plc_interface.reset()
                time.sleep(3)
                if not (r or m):
                    logger.info("PLC reset was successful")
                    break

                if (time.time() - start_time) > timeout:
                    with interfaces.StateInterface.update_state() as state:
                        state.exceptions_state.add_exception_state_item(
                            types.ExceptionStateItem(
                                origin=ORIGIN,
                                subject="PLC reset was required but did not work",
                            )
                        )
                    break
        else:
            logger.info("PLC reset is not needed")
            with interfaces.StateInterface.update_state() as state:
                state.exceptions_state.clear_exception_subject(
                    subject="PLC reset was required but did not work"
                )
