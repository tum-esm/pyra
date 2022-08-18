from typing import Any, Optional, TypedDict
import pydantic


class _OSStateDict(TypedDict):
    cpu_usage: Optional[list[float]]
    memory_usage: Optional[float]
    last_boot_time: Optional[str]
    filled_disk_space_fraction: Optional[float]


class StateDict(TypedDict):
    helios_indicates_good_conditions: Optional[bool]
    measurements_should_be_running: bool
    enclosure_plc_readings: dict
    os_state: _OSStateDict


class StateDictPartial(TypedDict, total=False):
    helios_indicates_good_conditions: Optional[int]
    measurements_should_be_running: bool
    enclosure_plc_readings: dict
    os_state: _OSStateDict


def validate_state_dict(o: Any, partial: bool = False) -> None:
    """
    Check, whether a given object is a correct StateDict
    Raises a pydantic.ValidationError if the object is invalid.

    This should always be used when loading the object from a
    JSON file!
    """
    if partial:
        _ValidationModel(partial=o)
    else:
        _ValidationModel(regular=o)


class _ValidationModel(pydantic.BaseModel):
    regular: Optional[StateDict]
    partial: Optional[StateDictPartial]
