from typing import TypedDict


class UploadMetaDict(TypedDict):
    complete: bool
    fileList: list[str]
    createdTime: float
    lastModifiedTime: float


class PartialUploadMetaDict(TypedDict, total=False):
    complete: bool
    fileList: list[str]
    createdTime: float
    lastModifiedTime: float


a: PartialUploadMetaDict = {
    "complete": False,
    "createdTime": 0.0,
    "lastModifiedTime": 0.0,
}
