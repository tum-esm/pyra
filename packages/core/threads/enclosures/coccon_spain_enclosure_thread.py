import threading
import time
from typing import Optional

import tum_esm_utils

from packages.core import interfaces, types, utils

from ..abstract_thread import AbstractThread


class COCCONSpainEnclosureThread(AbstractThread):
    """Thread interacting with the COCCON Spain Enclosure"""

    logger_origin = "coccon-spain-enclosure-thread"

    @staticmethod
    def should_be_running(config: types.Config, logger: utils.Logger) -> bool:
        """Based on the config, should the thread be running or not?"""

        return config.coccon_spain_enclosure is not None

    @staticmethod
    def get_new_thread_object(logs_lock: threading.Lock) -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(
            target=COCCONSpainEnclosureThread.main,
            daemon=True,
            args=(logs_lock,),
        )

    @staticmethod
    def main(logs_lock: threading.Lock, headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="coccon-spain-enclosure", lock=logs_lock)
        logger.info("Starting COCCON Spain Enclosure thread")

        enclosure_interface: Optional[interfaces.COCCONSpainEnclosureInterface] = None

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
                enclosure_config = config.coccon_spain_enclosure
                if enclosure_config is None:
                    logger.info("COCCON Spain Enclosure configuration not found, shutting down")
                    break

                if config.general.test_mode:
                    logger.info("COCCON Spain Enclosure thread is skipped in test mode")
                    time.sleep(15)
                    continue

                # CONNECTING TO PLC

                if enclosure_interface is None:
                    logger.debug("Connecting to Datalogger")
                    enclosure_interface = interfaces.COCCONSpainEnclosureInterface(
                        datalogger_ip=enclosure_config.ip, logger=logger
                    )
                else:
                    enclosure_interface.update_config(new_datalogger_ip=enclosure_config.ip)

                # UPDATING RECONNECTION STATE

                # now the PLC is connected - otherwise it would loop in the section above
                last_plc_connection_time = time.time()
                try:
                    # READING PLC

                    logger.debug("Reading Datalogger registers")
                    enclosure_state = enclosure_interface.read()

                    logger.debug("Updating enclosure state")
                    with interfaces.StateInterface.update_state(state_lock, logger) as s:
                        s.coccon_spain_enclosure_state = enclosure_state

                    logger.debug("Logging enclosure state")
                    utils.COCCONSpainEnclosureLogger.log(config, s)

                    # ENCLOSURE SPECIFIC LOGIC

                    # TODO:

                    # `exception_was_set` variable used to recude the number of state updates
                    if not exception_was_set:
                        exception_was_set = False
                        with interfaces.StateInterface.update_state(state_lock, logger) as s:
                            s.exceptions_state.clear_exception_origin(
                                origin="coccon-spain-enclosure"
                            )

                    # SLEEP

                    t2 = time.time()
                    sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                    logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)

                except interfaces.COCCONSpainEnclosureInterface.DataloggerError as e:
                    logger.error("Datalogger connection lost during interaction")
                    logger.exception(e)
                    enclosure_interface = None
                    logger.info("Waiting 60 seconds before retrying")
                    time.sleep(60)
                    continue

        except Exception as e:
            logger.exception(e)
            with interfaces.StateInterface.update_state(state_lock, logger) as s:
                s.exceptions_state.add_exception(origin="coccon-spain-enclosure", exception=e)
