import pydantic
from typing import Any, Union, Optional, TypedDict
from .plc_state import PlcStateDict, PlcStateDictPartial


class _OSStateDict(TypedDict):
    cpu_usage: Optional[list[float]]
    memory_usage: Optional[float]
    last_boot_time: Optional[str]
    filled_disk_space_fraction: Optional[float]


class StateDict(TypedDict):
    """TypedDict:

    ```ts
    {
        helios_indicates_good_conditions: boolean | null,
        measurements_should_be_running: boolean,
        enclosure_plc_readings: PlcStateDict,
        os_state: {
            cpu_usage: number[] | null,
            memory_usage: number | null,
            last_boot_time: string | null,
            filled_disk_space_fraction: number | null
        }
    }
    ```
    """

    helios_indicates_good_conditions: Optional[bool]
    measurements_should_be_running: bool
    enclosure_plc_readings: PlcStateDict
    os_state: _OSStateDict


class StateDictPartial(TypedDict, total=False):
    """TypedDict: like `StateDict`, but all fields are optional."""

    helios_indicates_good_conditions: Optional[int]
    measurements_should_be_running: bool
    enclosure_plc_readings: Union[PlcStateDict, PlcStateDictPartial]
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
