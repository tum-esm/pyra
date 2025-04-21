import datetime
import threading
import time
from typing import Optional

import circadian_scp_upload

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


class UploadThread(AbstractThread):
    """Thread for uploading data to a server via SCP.

    See https://github.com/dostuffthatmatters/circadian-scp-upload for
    a description of how this is implemented."""

    logger_origin = "upload-thread"
    last_measurement_time: Optional[datetime.datetime] = None

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        # only upload when upload is configured
        if config.upload is None:
            return False

        current_state = interfaces.StateInterface.load_state()
        should_be_running: bool = True
        if current_state.measurements_should_be_running:
            UploadThread.last_measurement_time = datetime.datetime.now()

        try:
            # don't upload while system is starting up
            assert current_state.measurements_should_be_running is not None
            assert current_state.position.sun_elevation is not None

            # don't upload when the upload or all streams are deactivated
            assert config.upload.is_active
            assert any([s.is_active for s in config.upload.streams])

            # (optional) don't upload during the day
            if config.upload.only_upload_at_night:
                assert current_state.position.sun_elevation <= 0

            # don't upload if system has been measuring in the last 10 minutes
            if config.upload.only_upload_when_not_measuring:
                if UploadThread.last_measurement_time is not None:
                    seconds_since_last_measurement = (
                        datetime.datetime.now() - UploadThread.last_measurement_time
                    ).total_seconds()
                    assert seconds_since_last_measurement >= 600
        except AssertionError:
            should_be_running = False

        if not should_be_running:
            if any([e.origin == "upload" for e in current_state.exceptions_state.current]):
                with interfaces.StateInterface.update_state() as s:
                    s.activity.upload_is_running = False
                    s.exceptions_state.clear_exception_origin("upload")

        return should_be_running

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=UploadThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="upload", just_print=headless)
        logger.info("Starting Upload thread")

        config = types.Config.load()
        assert config.upload is not None

        def upload_should_abort(silent: bool = False) -> bool:
            """Update the config from the main thread."""
            new_config = types.Config.load()
            upload_config_has_changed = new_config.upload != config.upload
            thread_should_not_be_running = not UploadThread.should_be_running(new_config)
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

                logger.info("starting upload")

                if config.general.test_mode:
                    logger.info("upload is skipped in test mode")
                    time.sleep(15)
                    continue

                with circadian_scp_upload.RemoteConnection(
                    config.upload.host.root,
                    config.upload.user,
                    config.upload.password,
                ) as remote_connection:
                    for stream in config.upload.streams:
                        if not stream.is_active:
                            logger.info(f"skipping upload of '{stream.label}'")
                            continue
                        with interfaces.StateInterface.update_state() as s:
                            s.activity.upload_is_running = True
                        logger.info(f"starting to upload '{stream.label}'")
                        logger.debug(f"stream config: {stream.model_dump_json()}")
                        circadian_scp_upload.DailyTransferClient(
                            remote_connection=remote_connection,
                            src_path=stream.src_directory.root,
                            dst_path=stream.dst_directory,
                            remove_files_after_upload=stream.remove_src_after_upload,
                            variant=stream.variant,
                            callbacks=circadian_scp_upload.UploadClientCallbacks(
                                dated_regex=stream.dated_regex,
                                log_info=lambda message: logger.debug(
                                    f"{stream.label} - {message}"
                                ),
                                log_error=lambda message: logger.error(
                                    f"{stream.label} - {message}"
                                ),
                                # callback that is called periodically during the upload
                                # process to check if the upload should be aborted
                                should_abort_upload=upload_should_abort,
                            ),
                        ).run()
                        with interfaces.StateInterface.update_state() as s:
                            s.activity.upload_is_running = False
                        if upload_should_abort():
                            logger.info("stopping upload thread")
                            return

                        logger.info(f"finished uploading '{stream.label}'")

                logger.info("finished upload")

                with interfaces.StateInterface.update_state() as s:
                    s.activity.upload_is_running = False  # not necessary, but ...
                    s.exceptions_state.clear_exception_origin("upload")

                # sleep 60 minutes until running again
                # stop thread if upload config has changed
                waiting_start_time = datetime.datetime.now()
                for i in range(60):
                    minutes_left = 60 - i
                    logger.info(
                        f"waiting {minutes_left} more minutes until looking for new files/directories"
                    )

                    for _ in range(6):
                        if upload_should_abort():
                            logger.info("stopping upload thread")
                            return

                        time.sleep(10)

                    # trying again at 1am because then new directories could be uploaded
                    if waiting_start_time.hour == 0 and datetime.datetime.now().hour == 1:
                        logger.info(
                            "abort waiting because there might be new data to upload at 1am"
                        )

            except Exception as e:
                logger.error(f"error in UploadThread: {repr(e)}")
                logger.exception(e)
                with interfaces.StateInterface.update_state() as s:
                    s.activity.upload_is_running = False
                    s.exceptions_state.add_exception(
                        origin="upload", exception=e, send_emails=False
                    )
                for i in range(20):
                    minutes_left = 20 - i
                    logger.info(
                        f"error in upload thread, waiting {minutes_left} more minutes until trying again"
                    )

                    for _ in range(6):
                        if upload_should_abort():
                            logger.info("stopping upload thread")
                            return

                        time.sleep(10)

                logger.info("stopping upload thread")
                return
