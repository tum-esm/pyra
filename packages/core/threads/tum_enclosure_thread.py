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

        while True:
            try:
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
                            with interfaces.StateInterface.update_state() as state:
                                state.exceptions_state.add_exception_state_item(
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
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.clear_exception_subject(
                        subject="Could not connect to PLC for 6 minutes"
                    )

                try:
                    # READING PLC

                    logger.info("Reading PLC")
                    plc_state = plc_interface.read()

                    logger.debug("Updating enclosure state")
                    with interfaces.StateInterface.update_state() as s:
                        s.tum_enclosure_state = plc_state

                    logger.debug("Logging enclosure state")
                    utils.TUMEnclosureLogger.log(config, s)

                    # RESETTING PLC

                    if plc_state.state.reset_needed == True:
                        logger.info("PLC indicates a reset is needed")
                        start_time = time.time()
                        while True:
                            if (time.time() - start_time) > 180:
                                with interfaces.StateInterface.update_state() as state:
                                    state.exceptions_state.add_exception_state_item(
                                        types.ExceptionStateItem(
                                            origin=ORIGIN,
                                            subject="PLC reset was required but did not work",
                                        )
                                    )
                                break

                            plc_interface.reset()
                            time.sleep(3)
                            if not plc_interface.reset_is_needed():
                                logger.info("PLC reset was successful")
                                plc_state.state.reset_needed = False
                                break
                    else:
                        with interfaces.StateInterface.update_state() as state:
                            state.exceptions_state.clear_exception_subject(
                                subject="PLC reset was required but did not work"
                            )

                    # CAMERA POWER CYCLE

                    # TODO:

                    # SPECTROMETER POWER

                    # TODO:

                    # SYNC COVER TO TRACKER

                    # TODO:
                    # wait here until cover is actually closed
                    # if sync to tracker was set, assert that it is still true (no emails though)

                    # SLEEP

                    t2 = time.time()
                    sleep_time = max(5, 40 - (t2 - t1))
                    logger.info(f"Sleeping {sleep_time} seconds")
                    time.sleep(sleep_time)

                except snap7.exceptions.Snap7Exception as e:
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
