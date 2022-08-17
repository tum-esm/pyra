from datetime import datetime
import hashlib
import json
import os
import shutil
import invoke
import paramiko
import time
import fabric
import re
from packages.core.utils import (
    ConfigInterface,
    Logger,
)
from .abstract_thread_base import AbstractThreadBase

logger = Logger(origin="upload")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


class InvalidUploadState(Exception):
    pass


class DirectoryUploadClient:
    """
    This is the client that is concerned with uploading one
    specific directory (YYYYMMDD). "self.run()" will perform
    the actual upload process.
    """

    def __init__(self, date_string: str, config: dict):
        self.connection = fabric.connection.Connection(
            f"{config['upload']['user']}@{config['upload']['host']}",
            connect_kwargs={"password": config["upload"]["password"]},
            connect_timeout=5,
        )
        self.transfer_process = fabric.transfer.Transfer(self.connection)

        self.date_string = date_string
        self.src_dir_path = os.path.join(config["upload"]["src_directory"], date_string)
        self.src_meta_path = os.path.join(self.src_dir_path, "upload-meta.json")
        assert os.path.isdir(self.src_dir_path), f"{self.src_dir_path} is not a directory"

        self.dst_dir_path = f"{config['upload']['dst_directory']}/{date_string}"
        self.dst_meta_path = f"{self.dst_dir_path}/upload-meta.json"
        assert self.transfer_process.is_remote_dir(
            config["upload"]["dst_directory"]
        ), f"remote {config['upload']['dst_directory']} is not a directory"

        self.meta_content: dict | None = None
        self.remove_src_after_upload: bool = config["upload"]["remove_src_after_upload"]

    def __initialize_remote_dir(self):
        """
        If the respective dst directory does not exist,
        create the directory and add a fresh upload-meta.json
        file to it looking like this: {
            "complete": false,
            "fileList": [],
            "createdTime": <unix-timestamp>,
            "lastModifiedTime": <unix-timestamp>
        }
        """
        if not self.transfer_process.is_remote_dir(self.dst_dir_path):
            self.connection.run(f"mkdir {self.dst_dir_path}")
            with open(self.src_meta_path, "w") as f:
                json.dump(
                    {
                        "complete": False,
                        "fileList": [],
                        "createdTime": round(time.time(), 3),
                        "lastModifiedTime": round(time.time(), 3),
                    },
                    f,
                    indent=4,
                )
            self.transfer_process.put(self.src_meta_path, self.dst_meta_path)

    def __get_remote_directory_checksum(self):
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
        remote_script_path = (
            self.config["upload"]["src_directory"] + "/get_upload_dir_checksum.py"
        )
        self.transfer_process.put(local_script_path, remote_script_path)

        try:
            self.connection.run("python3.10 --version", hide=True)
        except invoke.exceptions.UnexpectedExit:
            raise InvalidUploadState("python3.10 is not installed on the server")

        try:
            remote_command = f"python3.10 {remote_script_path} {self.src_dir_path}"
            a: invoke.runners.Result = self.connection.run(remote_command, hide=True)
            assert a.exited == 0
            return a.stdout.strip()
        except (invoke.exceptions.UnexpectedExit, AssertionError) as e:
            raise InvalidUploadState(
                f"could not execute remote command on server ({remote_command}): {e}"
            )

    def __get_local_directory_checksum(self):
        """
        Calculate checksum over all files listed in the
        upload-meta.json file. The same logic will run
        on the server - which also has a meta file in
        its dst directory with the same contents
        """
        hasher = hashlib.md5()
        for filename in sorted(self.meta_content["fileList"]):
            filepath = os.path.join(self.src_dir_path, filename)
            with open(filepath, "rb") as f:
                hasher.update(f.read())

        # output hashsum - with a status code of 0 the programs
        # stdout is a checksum, otherwise it is a traceback
        return hasher.hexdigest()

    def __fetch_meta(self):
        """
        Download the remote meta file to the local src directory
        """
        if os.path.isfile(self.src_meta_path):
            os.remove(self.src_meta_path)
        self.transfer_process.get(self.dst_meta_path, self.src_meta_path)
        try:
            assert os.path.isfile(self.src_meta_path)
            with open(self.src_meta_path, "r") as f:
                self.meta_content = json.load(f)
        except (AssertionError, json.JSONDecodeError) as e:
            raise InvalidUploadState(str(e))

    def __update_meta(self, new_meta_content_partial: dict):
        """
        Update the local upload-meta.json file and overwrite
        the meta file on the server
        """
        new_meta_content = {
            **self.meta_content,
            **new_meta_content_partial,
            "lastModifiedTime": round(time.time(), 3),
        }
        with open(self.src_meta_path, "w") as f:
            json.dump(new_meta_content, f, indent=4)
        self.transfer_process.put(self.src_meta_path, self.dst_meta_path)
        self.meta_content = new_meta_content

    def run(self):
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
        assert self.meta_content is not None

        # determine files present in src and dst directory
        # ifg files should be named like "<anything>YYYYMMDD<anything>.<digits>"
        ifg_file_pattern = re.compile("^.*" + self.date_string + ".*\.\d{2,6}$")
        src_file_set = set(
            [f for f in os.listdir(self.src_dir_path) if ifg_file_pattern.match(f)]
        )
        dst_file_set = set(self.meta_content["fileList"])

        # determine file differences between src and dst
        files_missing_in_dst = src_file_set.difference(dst_file_set)
        files_missing_in_src = dst_file_set.difference(src_file_set)
        if len(files_missing_in_src) > 0:
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
        # meta but present in the local directory. Every 25
        # files, upload the remote meta file on which files
        # have been uploaded
        upload_is_finished = False
        while not upload_is_finished:
            try:
                f = files_missing_in_dst.pop()
                self.transfer_process.put(
                    os.path.join(self.src_dir_path, f), f"{self.dst_dir_path}/{f}"
                )
                self.meta_content["fileList"].append(f)
            except KeyError:
                upload_is_finished = True

            if (self.meta_content["fileList"] % 25 == 0) or upload_is_finished:
                self.__update_meta({"fileList": self.meta_content["fileList"]})

        # raise an exception if the checksums do not match
        remote_checksum = self.__get_remote_directory_checksum()
        local_checksum = self.__get_local_directory_checksum()
        if remote_checksum != local_checksum:
            raise InvalidUploadState(
                f"checksums do not match, local={local_checksum} "
                + f"remote={remote_checksum}"
            )

        # only set meta.complet to True, when the checksums match
        self.__update_meta({"complete": True})
        logger.debug(f"successfully uploaded {self.date_string}")

        # only remove src if configured and checksums match
        if self.remove_src_after_upload:
            shutil.rmtree(self.src_dir_path)
            logger.debug("successfully removed source")
        else:
            logger.debug("skipping removal of source")

    def teardown(self):
        """close ssh and scp connection"""
        self.connection.close()

    @staticmethod
    def __is_valid_date(date_string: str):
        try:
            day_ending = datetime.strptime(f"{date_string} 23:59:59", "%Y%m%d %H:%M:%S")
            seconds_since_day_ending = (datetime.now() - day_ending).total_seconds()
            assert seconds_since_day_ending >= 3600
            return True
        except (ValueError, AssertionError):
            return False

    @staticmethod
    def get_directories_to_be_uploaded(ifg_src_path) -> list[str]:
        if not os.path.isdir(ifg_src_path):
            return []

        return list(
            filter(
                lambda f: os.path.isdir(os.path.join(ifg_src_path, f))
                and DirectoryUploadClient.__is_valid_date(f),
                os.listdir(ifg_src_path),
            )
        )


class UploadThread(AbstractThreadBase):
    """
    Thread for uploading all interferograms from a specific
    directory to a server via SSH. The local files will only
    be removed (optional) if the files on the server generate
    the same MD5 checksum as the local files.

    The source directory (where OPUS puts the interferograms)
    can be configured with config.upload.src_directory. OPUS's
    dst directory should be configured inside the macro file.

    The expected file structure looks like this:
    📁 <config.upload.src_directory>
        📁 <YYYYMMDD>
            📄 <interferogram 1>
            📄 <interferogram 2>
        📁 <YYYYMMDD>
            📄 <interferogram 1>
            📄 <interferogram 2>
        📁 ...
    """

    def __init__(self):
        super().__init__(logger)

    def should_be_running(self, config: dict) -> bool:
        """Should the thread be running? (based on config.upload)"""
        return (
            (not config["general"]["test_mode"])
            and (config["upload"] is not None)
            and (config["upload"]["is_active"])
        )

    def main(self):
        """Main entrypoint of the thread"""
        while True:
            config = ConfigInterface.read()

            src_dates_strings = DirectoryUploadClient.get_directories_to_be_uploaded(
                config["upload"]["src_directory"]
            )
            for src_date_string in src_dates_strings:

                # check for termination before processing each directory
                if not self.should_be_running(config):
                    return

                try:
                    client = DirectoryUploadClient(src_date_string)
                    client.run()
                except TimeoutError as e:
                    logger.error(f"could not reach host (uploading {src_date_string}): {e}")
                except paramiko.ssh_exception.AuthenticationException as e:
                    logger.error(f"failed to authenticate (uploading {src_date_string}): {e}")
                except InvalidUploadState as e:
                    logger.error(f"stuck in invalid state (uploading {src_date_string}): {e}")

                client.teardown()

            # Wait 10 minutes until checking all directories again
            time.sleep(600)
