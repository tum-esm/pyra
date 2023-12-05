import datetime
import threading
import time
import circadian_scp_upload
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils


class UploadThread(AbstractThread):
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
        return threading.Thread(target=UploadThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        logger = utils.Logger(origin="upload", just_print=headless)
        config = types.Config.load()
        assert config.upload is not None

        def upload_should_abort(silent: bool = False) -> bool:
            """Update the config from the main thread."""
            new_config = types.Config.load()
            upload_config_has_changed = new_config.upload != config.upload
            thread_should_not_be_running = not UploadThread.should_be_running(
                new_config
            )
            if not silent:
                if upload_config_has_changed:
                    logger.info("upload config has changed")
                if thread_should_not_be_running:
                    logger.info("upload thread should not be running")
            return upload_config_has_changed or thread_should_not_be_running

        while True:
            try:
                if upload_should_abort():
                    logger.info("stopping upload thread")
                    return

                interfaces.StateInterface.update_state(upload_is_running=True)
                logger.info("starting upload")

                with circadian_scp_upload.RemoteConnection(
                    config.upload.host.root,
                    config.upload.user,
                    config.upload.password,
                ) as remote_connection:

                    for stream in config.upload.streams:
                        if not stream.is_active:
                            logger.info(f"skipping upload of '{stream.label}'")
                            continue
                        logger.info(f"starting to upload '{stream.label}'")
                        logger.debug(
                            f"stream config: {stream.model_dump_json()}"
                        )
                        circadian_scp_upload.DailyTransferClient(
                            remote_connection=remote_connection,
                            src_path=stream.src_directory.root,
                            dst_path=stream.dst_directory,
                            remove_files_after_upload=stream.
                            remove_src_after_upload,
                            variant=stream.variant,
                            callbacks=circadian_scp_upload.
                            UploadClientCallbacks(
                                dated_regex=stream.dated_regex,
                                log_info=lambda message: logger.
                                debug(f"{stream.label} - {message}"),
                                log_error=lambda message: logger.
                                error(f"{stream.label} - {message}"),

                                # callback that is called periodically during the upload
                                # process to check if the upload should be aborted
                                should_abort_upload=upload_should_abort,
                            ),
                        ).run()

                        if upload_should_abort():
                            logger.info("stopping upload thread")
                            return

                        logger.info(f"finished uploading '{stream.label}'")

                logger.info("finished upload")
                interfaces.StateInterface.update_state(upload_is_running=False)

                # sleep 15 minutes until running again
                # stop thread if upload config has changed
                logger.info(
                    f"waiting 60 minutes until looking for new files/directories"
                )
                waiting_start_time = datetime.datetime.now()
                for i in range(30):
                    for j in range(12):
                        if upload_should_abort():
                            logger.info("stopping upload thread")
                            return

                        time.sleep(10)

                    # trying again at 1am because then new directories could be uploaded
                    if waiting_start_time.hour == 0 and datetime.datetime.now(
                    ).hour == 1:
                        logger.info(
                            f"Abort waiting because there might be new data to upload at 1am"
                        )

                    minutes_left = 60 - ((i + 1) * 2)
                    if minutes_left > 0:
                        logger.info(
                            f"waiting {minutes_left} more minutes until looking for new files/directories"
                        )

            except Exception as e:
                logger.error(f"error in UploadThread: {repr(e)}")
                logger.exception(e)
                logger.info(
                    f"waiting 20 minutes due to an error in the UploadThread, then restarting upload thread"
                )
                for i in range(10):
                    for j in range(12):
                        if upload_should_abort():
                            logger.info("stopping upload thread")
                            return

                        time.sleep(10)

                    minutes_left = 20 - ((i + 1) * 2)
                    if minutes_left > 0:
                        logger.info(
                            f"waiting {minutes_left} more minutes until looking "
                            + "for new files/directories"
                        )

                for i in range(5 * 6):
                    if upload_should_abort():
                        break
                    time.sleep(10)

                logger.info("stopping upload thread")
                return
