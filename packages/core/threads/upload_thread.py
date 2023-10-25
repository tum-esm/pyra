import datetime
import hashlib
import json
import os
import shutil
import threading
import deepdiff
import invoke
import time
import fabric.connection, fabric.transfer
import re
import pydantic
from packages.core import types, utils, interfaces

# TODO: add uploading to state

logger = utils.Logger(origin="upload")

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))

# when a connection error occurs, wait a few minutes until trying again
_CONNECTION_ERROR_IDLE_MINUTES = 5

# when an iteration is finished, wait a few minutes until checking again
_ITERATION_END_IDLE_MINUTES = 10


class InvalidUploadState(Exception):
    pass


class DirectoryUploadClient:
    """This is the client that is concerned with uploading one specific
    directory. run() will perform the actual upload process."""
    def __init__(
        self,
        date_string: str,
        src_path: str,
        dst_path: str,
        remove_files_after_upload: bool,
        connection: fabric.connection.Connection,
        transfer_process: fabric.transfer.Transfer,
    ) -> None:
        self.date_string = date_string
        self.src_path = src_path
        self.dst_path = dst_path[:-1] if dst_path.endswith("/") else dst_path
        self.remove_files_after_upload = remove_files_after_upload
        self.connection = connection
        self.transfer_process = transfer_process

        assert self.transfer_process.is_remote_dir(
            self.dst_path
        ), f"remote {self.dst_path} is not a directory"

        src_file_path = os.path.join(
            self.src_path, self.date_string, "upload-meta.json"
        )
        dst_file_path = os.path.join(
            f"{self.dst_path}/{self.date_string}/upload-meta.json"
        )

        # TODO: push error raising into init function
        dst_dir_path = f"{self.dst_path}/{self.date_string}"
        if self.transfer_process.is_remote_dir(dst_dir_path):
            try:
                self.meta = types.UploadMeta.init_from_remote(
                    src_file_path, dst_file_path, self.transfer_process
                )
            except (
                FileNotFoundError,
                AssertionError,
                json.JSONDecodeError,
                pydantic.ValidationError,
            ) as e:
                raise InvalidUploadState(str(e))
        else:
            self.connection.run(
                f"mkdir {dst_dir_path}", hide=True, in_stream=False
            )
            self.meta = types.UploadMeta.init_from_local(
                src_file_path, dst_file_path, self.transfer_process
            )

    def __get_remote_directory_checksum(self) -> str:
        """
        Calculate checksum over all files listed in the
        upload-meta.json file. The same logic will run
        on the local machine - which also has a meta file
        in its src directory with the same contents.

        This script requires the server to have Python
        3.10 installed and will raise an exception if its
        not present.
        """

        local_script_path = os.path.join(
            _PROJECT_DIR, "scripts", "get_upload_dir_checksum.py"
        )
        remote_script_path = f"{self.dst_path}/get_upload_dir_checksum.py"
        self.transfer_process.put(local_script_path, remote_script_path)

        try:
            self.connection.run(
                "python3.10 --version", hide=True, in_stream=False
            )
        except invoke.exceptions.UnexpectedExit:
            raise InvalidUploadState(
                "python3.10 is not installed on the server"
            )

        try:
            remote_command = (
                f"python3.10 {remote_script_path} {self.dst_path}/{self.date_string}"
            )
            a: invoke.runners.Result = self.connection.run(
                remote_command, hide=True, in_stream=False
            )
            assert a.exited == 0
            return a.stdout.strip()
        except (invoke.exceptions.UnexpectedExit, AssertionError) as e:
            raise InvalidUploadState(
                f"could not execute remote command on server ({remote_command}): {e}"
            )

    def __get_local_directory_checksum(self) -> str:
        """Calculate checksum over all files listed in the
        upload-meta.json file. The same logic will run
        on the server - which also has a meta file in
        its dst directory with the same contents"""

        hasher = hashlib.md5()
        for filename in sorted(self.meta.fileList):
            filepath = os.path.join(self.src_path, self.date_string, filename)
            with open(filepath, "rb") as f:
                hasher.update(f.read())

        # output hashsum - with a status code of 0 the programs
        # stdout is a checksum, otherwise it is a traceback
        return hasher.hexdigest()

    def run(self) -> None:
        """
        Perform the whole upload process for a given directory.

        1. If the respective remote directory doesn't exist, create it
        2. Download the current upload-meta.json file from the server
        3. Determine which files have not been uploaded yet
        4. Upload every file that is found locally but not in the remote
           meta. Update the remote meta every 25 uploaded files (reduces
           load and traffic).
        5. Test whether the checksums of "ifgs on server" and "local ifgs"
           are equal, raise an exception (and end the function) if the differ
        6. Indicate that the upload process is complete in remote meta
        7. Optionally remove local ifgs
        """

        # determine files present in src and dst directory
        # files should be named like "<anything>YYYYMMDD<anything>"
        ifg_file_pattern = re.compile("^.*" + self.date_string + ".*$")
        raw_src_files = os.listdir(
            os.path.join(self.src_path, self.date_string)
        )
        src_file_set = set([
            f for f in raw_src_files if ifg_file_pattern.match(f)
        ])
        dst_file_set = set(self.meta.fileList)

        # determine file differences between src and dst
        files_missing_in_dst = src_file_set.difference(dst_file_set)
        files_missing_in_src = dst_file_set.difference(src_file_set)
        if len(files_missing_in_src) > 0:
            # this happens, when the process fails during the src removal
            raise InvalidUploadState(
                f"files present in dst are missing in src: {files_missing_in_src}"
            )

        # if there are files that have not been uploaded,
        # assert that the remote meta also indicates an
        # incomplete upload state
        if (len(files_missing_in_dst) != 0) and self.meta.complete:
            raise InvalidUploadState(
                "missing files on dst but remote meta contains complete=True"
            )

        # upload every file that is missing in the remote
        # meta but present in the local directory
        for i, f in enumerate(sorted(files_missing_in_dst)):
            self.transfer_process.put(
                os.path.join(self.src_path, self.date_string, f),
                f"{self.dst_path}/{self.date_string}/{f}",
            )
            self.meta.fileList.append(f)

            # update the local meta in every loop, but only
            # sync the remote meta every 25 iterations
            sync_remote_meta = ((i + 1) % 25
                                == 0) or (i == len(files_missing_in_dst) - 1)
            self.meta.dump(
                transfer_process=self.
                transfer_process if sync_remote_meta else None
            )

        # raise an exception if the checksums do not match
        remote_checksum = self.__get_remote_directory_checksum()
        local_checksum = self.__get_local_directory_checksum()
        if remote_checksum != local_checksum:
            raise InvalidUploadState(
                f"checksums do not match, local={local_checksum} " +
                f"remote={remote_checksum}"
            )

        # only set meta.complete to True, when the checksums match
        self.meta.complete = True
        self.meta.dump(transfer_process=self.transfer_process)
        logger.info(f"Successfully uploaded {self.date_string}")

        # only remove src if configured and checksums match
        if self.remove_files_after_upload:
            shutil.rmtree(os.path.join(self.src_path, self.date_string))
            logger.debug("Successfully removed source")
        else:
            logger.debug("Skipping removal of source")

    @staticmethod
    def __is_valid_date(date_string: str) -> bool:
        try:
            day_ending = datetime.datetime.strptime(
                f"{date_string} 23:59:59", "%Y%m%d %H:%M:%S"
            )
            seconds_since_day_ending = (datetime.datetime.now() -
                                        day_ending).total_seconds()
            assert seconds_since_day_ending >= 3600
            return True
        except (ValueError, AssertionError):
            return False

    @staticmethod
    def get_directories_to_be_uploaded(data_path: str) -> list[str]:
        if not os.path.isdir(data_path):
            return []

        return list(
            filter(
                lambda f: os.path.isdir(os.path.join(data_path, f)) and
                DirectoryUploadClient.__is_valid_date(f),
                os.listdir(data_path),
            )
        )


class UploadThread:
    """Thread for uploading all interferograms from a
    specific directory to a server via SSH.

    The local files will only be removed (optional) if the
    files on the server generate the same MD5 checksum as
    the local files.

    The source directory where OPUS puts the interferograms
    can be configured with config.upload.src_directory_ifgs.
    OPUS's output directory should be configured inside the
    macro file.

    The expected file structure looks like this:

    ```
    📁 srcdir/dstdir
        📁 YYYYMMDD
            📄 filename1
            📄 filename2
        📁 YYYYMMDD
            📄 filename1
            📄 filename2
        📁 ...
    ```

    Each YYYYMMDD folder will be uploaded independently. During
    its upload the process will store its progress inside a file
    "YYYYMMDD/upload-meta.json" (locally and remotely).

    The upload-meta.json file looks like this:

    ```json
    {
        "complete": bool,
        "fileList": [filename1, filename2, ...],
        "createdTime": float,
        "lastModifiedTime": float
    }
    ```

    This function only does one loop in headless mode.
    """
    def __init__(self, config: types.Config) -> None:
        self.__thread = threading.Thread(target=UploadThread.main)
        self.__logger: utils.Logger = utils.Logger(origin="upload")
        self.config: types.Config = config
        self.is_initialized = False

    def update_thread_state(self, new_config: types.Config) -> None:
        """
        Make sure that the thread loop is (not) running,
        based on config.upload
        """
        self.config = new_config
        should_be_running = (new_config.upload is not None
                            ) and (not new_config.general.test_mode)

        if should_be_running and (not self.is_initialized):
            self.__logger.info("Starting the thread")
            self.is_initialized = True
            self.__thread.start()

        # set up a new thread instance for the next time the thread should start
        if self.is_initialized:
            if self.__thread.is_alive():
                self.__logger.debug("Thread is alive")
            else:
                self.__logger.debug("Thread is not alive, running teardown")
                self.__thread.join()
                self.__thread = threading.Thread(target=UploadThread.main)
                self.is_initialized = False

    @staticmethod
    def main(headless: bool = False) -> None:
        """
        Main entrypoint of the thread

        headless mode = don't write to log files, print to console
        """
        global logger

        if headless:
            logger = utils.Logger(origin="upload", just_print=True)

        while True:
            try:
                logger.info("Starting iteration")
                config = types.Config.load()

                if config.upload is None:
                    logger.info("Ending thread (upload config is null)")
                    return
                if config.general.test_mode:
                    logger.info("Ending thread (Pyra is in test mode)")
                    return

                try:
                    upload_is_complete = UploadThread.upload_all_files(config)
                except interfaces.SSHInterface.ConnectionError as e:
                    logger.error(f"could not connect to host: {e}")
                    if not headless:
                        logger.info(
                            f"waiting {_CONNECTION_ERROR_IDLE_MINUTES} minutes"
                        )
                        time.sleep(_CONNECTION_ERROR_IDLE_MINUTES * 60)
                        continue

                if headless:
                    return

                if upload_is_complete:
                    logger.debug(
                        f"Finished iteration, sleeping {_ITERATION_END_IDLE_MINUTES} minutes"
                    )
                    time.sleep(_ITERATION_END_IDLE_MINUTES * 60)
            except Exception as e:
                logger.error(f"Error inside upload thread: {e}")
                logger.exception(e)
                return

    @staticmethod
    def upload_all_files(config: types.Config) -> bool:
        """
        Returns True if all file uploads have been finished. Returns False
        if the config has change during upload -> restart with new parameters.
        """

        upload_config = config.upload
        assert upload_config is not None

        # this will be quite simplified by the "Update: Upload Improvements"
        categories = []
        categories += ["helios"] if upload_config.upload_helios else []
        categories += ["ifgs"] if upload_config.upload_ifgs else []

        for category in categories:
            if category == "helios":
                src_path = os.path.join(_PROJECT_DIR, "logs", "helios")
                dst_path = upload_config.dst_directory_helios
                remove_files_after_upload = upload_config.remove_src_helios_after_upload
            else:
                src_path = upload_config.src_directory_ifgs
                dst_path = upload_config.dst_directory_ifgs
                remove_files_after_upload = upload_config.remove_src_ifgs_after_upload

            src_date_strings = DirectoryUploadClient.get_directories_to_be_uploaded(
                src_path
            )
            for date_string in src_date_strings:
                # abort the upload process when upload config changes
                new_config = types.Config.load()
                difference = deepdiff.DeepDiff(upload_config, new_config.upload)
                if len(difference) != 0:
                    logger.info("Change in config.upload has been detected")
                    return False

                with interfaces.SSHInterface.use(config) as (
                    connection, transfer_process
                ):
                    try:
                        logger.info(f"Starting to process {date_string}")
                        DirectoryUploadClient(
                            date_string,
                            src_path,
                            dst_path,
                            remove_files_after_upload,
                            connection,
                            transfer_process,
                        ).run()
                    except InvalidUploadState as e:
                        logger.error(
                            f"uploading {date_string} is stuck in invalid state: {e}"
                        )

        return True
