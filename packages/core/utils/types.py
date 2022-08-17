from typing import Optional, TypedDict


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


class PersistentStateDict(TypedDict):
    active_opus_macro_id: Optional[int]
    current_exceptions: list[str]


class PartialPersistentStateDict(TypedDict, total=False):
    active_opus_macro_id: Optional[int]
    current_exceptions: list[str]
