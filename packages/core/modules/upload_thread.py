from datetime import datetime
import json
import os
import queue
import shutil
import paramiko
import threading
import time
import fabric
from packages.core.utils import (
    ConfigInterface,
    Logger,
)

logger = Logger(origin="upload")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


class InvalidUploadState(Exception):
    pass


class DirectoryUploadClient:
    def __init__(self, dirname: str, config: dict):
        self.connection = fabric.connection.Connection(
            f"{config['upload']['user']}@{config['upload']['host']}",
            connect_kwargs={"password": config["upload"]["password"]},
            connect_timeout=5,
        )
        self.transfer_process = fabric.transfer.Transfer(self.connection)

        self.src_dir_path = os.path.join(config["upload"]["src_directory"], dirname)
        self.src_meta_path = os.path.join(self.src_dir_path, "upload-meta.json")
        assert os.path.isdir(self.src_dir_path), f"{self.src_dir_path} is not a directory"

        self.dst_dir_path = f"{config['upload']['dst_directory']}/{dirname}"
        self.dst_meta_path = f"{self.dst_dir_path}/upload-meta.json"
        assert self.transfer_process.is_remote_dir(
            config["upload"]["dst_directory"]
        ), f"remote {config['upload']['dst_directory']} is not a directory"

        self.meta_content: dict | None = None

    def create_remote_dir(self):
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

    def fetch_meta(self):
        if os.path.isfile(self.src_meta_path):
            os.remove(self.src_meta_path)
        self.transfer_process.get(self.dst_meta_path, self.src_meta_path)
        try:
            assert os.path.isfile(self.src_meta_path)
            with open(self.src_meta_path, "r") as f:
                self.meta_content = json.load(f)
        except (AssertionError, json.JSONDecodeError) as e:
            # TODO: log/report this exception and continue with other directories
            raise InvalidUploadState(str(e))

    def update_meta(self, new_meta_content: dict):
        new_meta_content = {
            **new_meta_content,
            "lastModifiedTime": round(time.time(), 3),
        }
        with open(self.src_meta_path, "w") as f:
            json.dump(new_meta_content, f, indent=4)
        self.transfer_process.put(self.src_meta_path, self.dst_meta_path)
        self.meta_content = new_meta_content

    def run(self):
        # possibly initialize remote dir, fetch remote meta
        if not self.transfer_process.is_remote_dir(self.dst_dir_path):
            self.create_remote_dir()
        self.fetch_meta()
        assert self.meta_content is not None

        # determine files missing in dst
        src_file_set = set(os.listdir(self.src_dir_path))
        src_file_set.remove("upload-meta.json")
        dst_file_set = set(self.meta_content["fileList"])
        files_missing_in_dst = src_file_set.difference(dst_file_set)

        # if there are files that have not been uploaded,
        # assert that the remote meta also indicates an
        # incomplete upload state
        if len(files_missing_in_dst) != 0:
            if self.meta_content["complete"]:
                raise InvalidUploadState(
                    "there are missing files but remote " + "meta contains complete=True"
                )

        # upload every file that is missing in the remote
        # meta but present in the local directory. Every 25
        # files, upload the remote meta file on which files
        # have been uploaded
        upload_count = 0
        uploaded_files: list[str] = []
        while True:
            try:
                f = files_missing_in_dst.pop()
            except KeyError:
                break
            self.transfer_process.put(
                os.path.join(self.src_dir_path, f), f"{self.dst_dir_path}/{f}"
            )
            uploaded_files.append(f)
            upload_count += 1
            if upload_count % 25 == 0:
                self.update_meta(
                    {
                        **self.meta_content,
                        "fileList": [*(self.meta_content["fileList"]), *uploaded_files],
                    }
                )
                uploaded_files = []

        # update remote meta with the final files and set
        # "complete" to True. This indicates that
        self.update_meta(
            {
                **self.meta_content,
                "complete": True,
                "fileList": [*(self.meta_content["fileList"]), *uploaded_files],
            }
        )

        # TODO: make sure all copying was successful - maybe
        #       use a checksum over a temporary tarball
        # TODO: make the deletion of src optional (boolean in config)
        # shutil.rmtree(self.src_dir_path)

        # close ssh and scp connection
        self.connection.close()


def is_valid_date(date_string: str):
    try:
        day_ending = datetime.strptime(f"{date_string} 23:59:59", "%Y%m%d %H:%M:%S")
        seconds_since_day_ending = (datetime.now() - day_ending).total_seconds()
        assert seconds_since_day_ending >= 3600
        return True
    except (ValueError, AssertionError):
        return False


def get_directories_to_be_uploaded(ifg_src_path) -> list[str]:
    if not os.path.isdir(ifg_src_path):
        return []

    return list(
        filter(
            lambda f: os.path.isdir(os.path.join(ifg_src_path, f)) and is_valid_date(f),
            os.listdir(ifg_src_path),
        )
    )


class UploadThread:
    def __init__(self):
        self.__thread = None
        self.__shared_queue = None

    def start(self):
        """
        Start the thread using the threading library
        """
        logger.info("Starting thread")
        self.__shared_queue = queue.Queue()
        self.__thread = threading.Thread(target=UploadThread.main, args=(self.__shared_queue,))
        self.__thread.start()

    def is_running(self):
        return self.__thread is not None

    def stop(self):
        """
        Send a stop-signal to the thread and wait for its termination
        """

        assert self.__shared_queue is not None

        logger.info("Sending termination signal")
        self.__shared_queue.put("stop")

        logger.info("Waiting for thread to terminate")
        self.__thread.join()
        self.__thread = None
        self.__shared_queue = None

        logger.info("Stopped the thread")

    @staticmethod
    def main(shared_queue: queue.Queue):
        while True:
            config = ConfigInterface.read()

            # Check for termination
            try:
                if (
                    (config["upload"] is None)
                    or (not config["upload"]["is_active"])
                    or (shared_queue.get(block=False) == "stop")
                ):
                    break
            except queue.Empty:
                pass

            start_time = time.time()

            for src_date_string in get_directories_to_be_uploaded(
                config["upload"]["src_directory"]
            ):
                try:
                    DirectoryUploadClient(src_date_string).run()
                    logger.info(f"successfully uploaded data from {src_date_string}")
                except TimeoutError as e:
                    logger.error(f"could not reach host (uploading {src_date_string}): {e}")
                except paramiko.ssh_exception.AuthenticationException as e:
                    logger.error(f"failed to authenticate (uploading {src_date_string}): {e}")
                except InvalidUploadState as e:
                    logger.error(f"stuck in invalid state (uploading {src_date_string}): {e}")

            # TODO: 6. Figure out where ifgs lie on systems
            # TODO: 7. Implement datalogger upload

            elapsed_time = time.time() - start_time
            time_to_wait = 5 - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
