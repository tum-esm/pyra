from typing import Any, Optional, TypedDict
import pydantic


class ConfigDict(TypedDict):
    general: dict
    opus: dict
    camtracker: dict
    error_email: dict
    measurement_decision: dict
    measurement_triggers: dict
    tum_plc: Optional[dict]
    helios: Optional[dict]
    upload: Optional[dict]


class ConfigDictPartial(TypedDict, total=False):
    general: dict
    opus: dict
    camtracker: dict
    error_email: dict
    measurement_decision: dict
    measurement_triggers: dict
    tum_plc: Optional[dict]
    helios: Optional[dict]
    upload: Optional[dict]


def validate_config_dict(o: Any, partial: bool = False) -> None:
    """
    Check, whether a given object is a correct ConfigDict
    Raises a pydantic.ValidationError if the object is invalid.

    This should always be used when loading the object from a
    JSON file!
    """
    if partial:
        _ValidationModel(partial=o)
    else:
        _ValidationModel(regular=o)


class _ValidationModel(pydantic.BaseModel):
    regular: Optional[ConfigDict]
    partial: Optional[ConfigDictPartial]
