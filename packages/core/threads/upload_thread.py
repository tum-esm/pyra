from datetime import datetime
import hashlib
import json
import os
import shutil
import threading
from typing import Optional
import deepdiff
import invoke
import time
import fabric.connection, fabric.transfer
import re
import pydantic
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="upload")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))

# when a connection error occurs, wait a few minutes until trying again
CONNECTION_ERROR_IDLE_MINUTES = 5

# when an iteration is finished, wait a few minutes until checking again
ITERATION_END_IDLE_MINUTES = 10


class InvalidUploadState(Exception):
    pass


class DirectoryUploadClient:
    """
    This is the client that is concerned with uploading one specific
    directory. run() will perform the actual upload process.
    """

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

        self.src_meta_path = os.path.join(self.src_path, self.date_string, "upload-meta.json")
        self.dst_meta_path = os.path.join(
            f"{self.dst_path}/{self.date_string}/upload-meta.json"
        )

        assert self.transfer_process.is_remote_dir(
            self.dst_path
        ), f"remote {self.dst_path} is not a directory"

        self.meta_content: types.UploadMetaDict = {
            "complete": False,
            "fileList": [],
            "createdTime": round(time.time(), 3),
            "lastModifiedTime": round(time.time(), 3),
        }

    def __initialize_remote_dir(self) -> None:
        """
        If the respective dst directory does not exist,
        create the directory and add a fresh upload-meta.json
        file to it.
        """
        dst_dir_path = f"{self.dst_path}/{self.date_string}"
        if not self.transfer_process.is_remote_dir(dst_dir_path):
            self.connection.run(f"mkdir {dst_dir_path}", hide=True, in_stream=False)
            with open(self.src_meta_path, "w") as f:
                json.dump(self.meta_content, f, indent=4)
            self.transfer_process.put(self.src_meta_path, self.dst_meta_path)

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

        local_script_path = os.path.join(PROJECT_DIR, "scripts", "get_upload_dir_checksum.py")
        remote_script_path = f"{self.dst_path}/get_upload_dir_checksum.py"
        self.transfer_process.put(local_script_path, remote_script_path)

        try:
            self.connection.run("python3.10 --version", hide=True, in_stream=False)
        except invoke.exceptions.UnexpectedExit:
            raise InvalidUploadState("python3.10 is not installed on the server")

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
        """
        Calculate checksum over all files listed in the
        upload-meta.json file. The same logic will run
        on the server - which also has a meta file in
        its dst directory with the same contents
        """

        hasher = hashlib.md5()
        for filename in sorted(self.meta_content["fileList"]):
            filepath = os.path.join(self.src_path, self.date_string, filename)
            with open(filepath, "rb") as f:
                hasher.update(f.read())

        # output hashsum - with a status code of 0 the programs
        # stdout is a checksum, otherwise it is a traceback
        return hasher.hexdigest()

    def __fetch_meta(self) -> None:
        """
        Download the remote meta file to the local src directory
        """

        if os.path.isfile(self.src_meta_path):
            os.remove(self.src_meta_path)
        self.transfer_process.get(self.dst_meta_path, self.src_meta_path)
        try:
            assert os.path.isfile(self.src_meta_path)
            with open(self.src_meta_path, "r") as f:
                new_meta_content = json.load(f)
                types.validate_upload_meta_dict(new_meta_content)
                self.meta_content = new_meta_content
        except (AssertionError, json.JSONDecodeError, pydantic.ValidationError) as e:
            raise InvalidUploadState(str(e))

    def __update_meta(
        self,
        update: Optional[types.UploadMetaDictPartial] = None,
        sync_remote_meta: bool = True,
    ) -> None:
        """
        Update the local upload-meta.json file and overwrite
        the meta file on the server when sync==True
        """

        if update is not None:
            self.meta_content.update(update)
            self.meta_content.update({"lastModifiedTime": round(time.time(), 3)})
            with open(self.src_meta_path, "w") as f:
                json.dump(self.meta_content, f, indent=4)

        if sync_remote_meta:
            self.transfer_process.put(self.src_meta_path, self.dst_meta_path)

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

        self.__initialize_remote_dir()
        self.__fetch_meta()

        # determine files present in src and dst directory
        # files should be named like "<anything>YYYYMMDD<anything>"
        ifg_file_pattern = re.compile("^.*" + self.date_string + ".*$")
        raw_src_files = os.listdir(os.path.join(self.src_path, self.date_string))
        src_file_set = set([f for f in raw_src_files if ifg_file_pattern.match(f)])
        dst_file_set = set(self.meta_content["fileList"])

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
        if (len(files_missing_in_dst) != 0) and self.meta_content["complete"]:
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
            # update the local meta in every loop, but only
            # sync the remote meta every 25 iterations
            self.__update_meta(
                update={"fileList": [*self.meta_content["fileList"], f]},
                sync_remote_meta=(i % 25 == 0),
            )

        # make sure that the remote meta is synced
        self.__update_meta()

        # raise an exception if the checksums do not match
        remote_checksum = self.__get_remote_directory_checksum()
        local_checksum = self.__get_local_directory_checksum()
        if remote_checksum != local_checksum:
            raise InvalidUploadState(
                f"checksums do not match, local={local_checksum} "
                + f"remote={remote_checksum}"
            )

        # only set meta.complete to True, when the checksums match
        self.__update_meta(update={"complete": True})
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
            day_ending = datetime.strptime(f"{date_string} 23:59:59", "%Y%m%d %H:%M:%S")
            seconds_since_day_ending = (datetime.now() - day_ending).total_seconds()
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
                lambda f: os.path.isdir(os.path.join(data_path, f))
                and DirectoryUploadClient.__is_valid_date(f),
                os.listdir(data_path),
            )
        )


class UploadThread:
    """
    Thread for uploading all interferograms from a specific
    directory to a server via SSH. The local files will only
    be removed (optional) if the files on the server generate
    the same MD5 checksum as the local files.

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

    def __init__(self, config: types.ConfigDict) -> None:
        self.__thread = threading.Thread(target=UploadThread.main)
        self.__logger: utils.Logger = utils.Logger(origin="upload")
        self.config: types.ConfigDict = config
        self.is_initialized = False

    def update_thread_state(self, new_config: types.ConfigDict) -> None:
        """
        Make sure that the thread loop is (not) running,
        based on config.upload
        """
        self.config = new_config
        should_be_running = (new_config["upload"] is not None) and (
            not new_config["general"]["test_mode"]
        )

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
                config = interfaces.ConfigInterface.read()

                if config["upload"] is None:
                    logger.info("Ending thread (upload config is null)")
                    return
                if config["general"]["test_mode"]:
                    logger.info("Ending thread (Pyra is in test mode)")
                    return

                try:
                    upload_is_complete = UploadThread.upload_all_files(config)
                except interfaces.SSHInterface.ConnectionError as e:
                    logger.error(f"could not connect to host: {e}")
                    if not headless:
                        logger.info(f"waiting {CONNECTION_ERROR_IDLE_MINUTES} minutes")
                        time.sleep(CONNECTION_ERROR_IDLE_MINUTES * 60)
                        continue

                if headless:
                    return

                if upload_is_complete:
                    logger.debug(
                        f"Finished iteration, sleeping {ITERATION_END_IDLE_MINUTES} minutes"
                    )
                    time.sleep(ITERATION_END_IDLE_MINUTES * 60)
            except Exception as e:
                logger.error(f"Error inside upload thread: {e}")
                logger.exception(e)
                return

    @staticmethod
    def upload_all_files(config: types.ConfigDict) -> bool:
        """
        Returns True if all file uploads have been finished. Returns False
        if the config has change during upload -> restart with new parameters.
        """

        upload_config = config["upload"]
        assert upload_config is not None

        # this will be quite simplified by the "Update: Upload Improvements"
        categories = []
        categories += ["helios"] if upload_config["upload_helios"] else []
        categories += ["ifgs"] if upload_config["upload_ifgs"] else []

        for category in categories:
            if category == "helios":
                src_path = os.path.join(PROJECT_DIR, "logs", "helios")
                dst_path = upload_config["dst_directory_helios"]
                remove_files_after_upload = upload_config["remove_src_helios_after_upload"]
            else:
                src_path = upload_config["src_directory_ifgs"]
                dst_path = upload_config["dst_directory_ifgs"]
                remove_files_after_upload = upload_config["remove_src_ifgs_after_upload"]

            src_date_strings = DirectoryUploadClient.get_directories_to_be_uploaded(src_path)
            for date_string in src_date_strings:

                # abort the upload process when upload config changes
                new_config = interfaces.ConfigInterface.read()
                difference = deepdiff.DeepDiff(upload_config, new_config["upload"])
                if len(difference) != 0:
                    logger.info("Change in config.upload has been detected")
                    return False

                with interfaces.SSHInterface.use(config) as (
                    connection,
                    transfer_process,
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
                        logger.error(f"uploading {date_string} is stuck in invalid state: {e}")

        return True
