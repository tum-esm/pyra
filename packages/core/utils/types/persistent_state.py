from typing import Any, Optional, TypedDict
import pydantic


class PersistentStateDict(TypedDict):
    active_opus_macro_id: Optional[int]
    current_exceptions: list[str]


class PersistentStateDictPartial(TypedDict, total=False):
    active_opus_macro_id: Optional[int]
    current_exceptions: list[str]


def validate_persistent_state_dict(o: Any, partial: bool = False) -> None:
    """
    Check, whether a given object is a correct PersistentStateDict
    Raises a pydantic.ValidationError if the object is invalid.

    This should always be used when loading the object from a
    JSON file!
    """
    if partial:
        _ValidationModel(partial=o)
    else:
        _ValidationModel(regular=o)


class _ValidationModel(pydantic.BaseModel):
    regular: Optional[PersistentStateDict]
    partial: Optional[PersistentStateDictPartial]
