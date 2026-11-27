import threading
import time

import tum_esm_utils

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


class ExceptionEmailThread(AbstractThread):
    """Send exception notifications independently of the main loop and producers."""

    logger_origin = "exception-email-thread"

    @staticmethod
    def should_be_running(config: types.Config, logger: utils.Logger) -> bool:
        return True

    @staticmethod
    def get_new_thread_object(logs_lock: threading.Lock) -> threading.Thread:
        return threading.Thread(target=ExceptionEmailThread.main, daemon=True, args=(logs_lock,))

    @staticmethod
    def main(logs_lock: threading.Lock, headless: bool = False) -> None:
        logger = utils.Logger(origin="exception-email", lock=logs_lock, just_print=headless)
        logger.info("Starting Exception Email thread")
        state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
            filepath=interfaces.state_interface.STATE_LOCK_PATH,
            timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
            poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
        )

        while True:
            try:
                config = types.Config.load(ignore_path_existence=True)
                interfaces.ExceptionsInterface.update_exception_notifications(
                    state_lock, logger, config
                )
                time.sleep(config.general.seconds_per_core_iteration)
            except Exception as e:
                logger.exception(e)
                logger.error("Exception notification iteration failed, waiting 15 seconds")
                time.sleep(15)
