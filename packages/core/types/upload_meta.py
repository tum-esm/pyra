from __future__ import annotations
import json
import os
import time
from typing import Optional
import pydantic
import fabric.transfer


class UploadMeta(pydantic.BaseModel):
    src_file_path: str
    dst_file_path: str
    complete: bool
    fileList: list[str]
    createdTime: Optional[float]
    lastModifiedTime: Optional[float]

    def dump(self, transfer_process: Optional[fabric.transfer.Transfer] = None) -> None:
        """dumps the JSON file, and transfer it to remote if transfer_process is not None"""
        with open(self.src_file_path, "w") as f:
            json.dump(self.model_dump(exclude={"src_file_path", "dst_file_path"}), f, indent=4)
        if transfer_process is not None:
            transfer_process.put(self.src_file_path, self.dst_file_path)

    @staticmethod
    def init_from_local(
        src_file_path: str,
        dst_file_path: str,
        transfer_process: fabric.transfer.Transfer,
    ) -> UploadMeta:
        meta = UploadMeta(
            src_file_path=src_file_path,
            dst_file_path=dst_file_path,
            complete=False,
            fileList=[],
            createdTime=round(time.time(), 3),
            lastModifiedTime=round(time.time(), 3),
        )
        meta.dump(transfer_process=transfer_process)
        return meta

    @staticmethod
    def init_from_remote(
        src_file_path: str,
        dst_file_path: str,
        transfer_process: fabric.transfer.Transfer,
    ) -> UploadMeta:
        if os.path.isfile(src_file_path):
            os.remove(src_file_path)
        transfer_process.get(dst_file_path, src_file_path)
        with open(src_file_path, "r") as f:
            return UploadMeta(**json.load(f))
