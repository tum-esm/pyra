from typing import Any, Optional, TypedDict

import pydantic


class UploadMetaTypes:
    @staticmethod
    class Dict(TypedDict):
        complete: bool
        fileList: list[str]
        createdTime: float
        lastModifiedTime: float

    @staticmethod
    class PartialDict(TypedDict, total=False):
        complete: bool
        fileList: list[str]
        createdTime: float
        lastModifiedTime: float

    @staticmethod
    def validate_object(o: Any, partial: bool = False) -> None:
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
    regular: Optional[UploadMetaTypes.Dict]
    partial: Optional[UploadMetaTypes.PartialDict]
