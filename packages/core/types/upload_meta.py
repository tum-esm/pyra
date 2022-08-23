import pydantic
from typing import Any, Optional, TypedDict


class UploadMetaDict(TypedDict):
    complete: bool
    fileList: list[str]
    createdTime: float
    lastModifiedTime: float


class UploadMetaDictPartial(TypedDict, total=False):
    complete: bool
    fileList: list[str]
    createdTime: float
    lastModifiedTime: float


def validate_upload_meta_dict(o: Any, partial: bool = False) -> None:
    """
    Check, whether a given object is a correct UploadMetaDict
    Raises a pydantic.ValidationError if the object is invalid.

    This should always be used when loading the object from a
    JSON file!
    """
    if partial:
        _ValidationModel(partial=o)
    else:
        _ValidationModel(regular=o)


class _ValidationModel(pydantic.BaseModel):
    regular: Optional[UploadMetaDict]
    partial: Optional[UploadMetaDictPartial]
