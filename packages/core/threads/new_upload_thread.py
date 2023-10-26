import threading
import time
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils


class NewUploadThread(AbstractThread):
    """Thread for uploading data to a server via SCP.
    
    See https://github.com/dostuffthatmatters/circadian-scp-upload for
    a description of how this is implemented."""
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""
        upload_is_configured = config.upload is not None
        not_in_test_mode = not config.general.test_mode
        not_measuring = not interfaces.StateInterface.load_state(
        ).measurements_should_be_running

        return all([upload_is_configured, not_in_test_mode, not_measuring])

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=NewUploadThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        logger = utils.Logger(origin="upload", just_print=headless)
        config = types.Config.load()

        while True:
            try:
                # Check for termination
                if not NewUploadThread.should_be_running(config):
                    return

                # TODO: try to connect to server
                # TODO: for target in targets: upload
                # TODO: disconnect from server
                # TODO: sleep 15 minutes until running again

            except Exception as e:
                logger.error(f"error in UploadThread: {repr(e)}")
                logger.exception(e)
                logger.info(f"sleeping 30 seconds, reinitializing UploadThread")
                time.sleep(30)
