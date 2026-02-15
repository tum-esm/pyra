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

        logger = utils.Logger(origin="aemet-enclosure", lock=logs_lock)
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
                    enclosure_state = enclosure_interface.read(
                        immediate_write_to_central_state=False
                    )

                    logger.debug("Updating enclosure state")
                    with interfaces.StateInterface.update_state(state_lock, logger) as s:
                        s.aemet_enclosure_state = enclosure_state

                    logger.debug("Logging enclosure state")
                    utils.AEMETEnclosureLogger.log(config, s)

                    # ENCLOSURE SPECIFIC LOGIC

                    # TODO: if controlled by user, dont do anything else

                    # TODO: if in auto mode, set auto mode to 0

                    # TODO: if enhanced security mode is 0, set it to 1

                    # TODO: if spectrometer power is unknown, fetch spectrometer power

                    # TODO: if toggle spectrometer power is enabled, toggle spectrometer power if night

                    # TODO: if closed due to weather conditions, don't do anything else

                    # TODO: if opened due to high internal humidity, don't do anything else

                    # TODO: if alert is non-zero, don't do anything else

                    # TODO: if should measure but cover is closed, open cover

                    # TODO: if should not measure but cover is open, close cover

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
