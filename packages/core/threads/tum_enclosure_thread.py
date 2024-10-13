import threading
import time
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

        # TODO: implement #232

        logger = utils.Logger(origin=ORIGIN)

        while True:
            try:
                t1 = time.time()

                logger.info("Loading configuration file")
                config = types.Config.load()

                # TODO

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, 60 - (t2 - t1))
                logger.info(f"Sleeping {sleep_time} seconds")
                time.sleep(sleep_time)

            except Exception as e:
                logger.exception(e)
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.add_exception(origin=ORIGIN, exception=e)
