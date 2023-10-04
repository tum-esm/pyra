from __future__ import annotations
import json
import os
import pydantic
from typing import Literal, Optional
from .plc_state import PlcState

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "logs", "state.json")
_PERSISTENT_STATE_FILE_PATH = os.path.join(
    _PROJECT_DIR, "logs", "persistent-state.json"
)


class _OSStateDict(pydantic.BaseModel):
    cpu_usage: Optional[list[float]] = None
    memory_usage: Optional[float] = None
    last_boot_time: Optional[str] = None
    filled_disk_space_fraction: Optional[float] = None


class PyraCoreState(pydantic.BaseModel):
    helios_indicates_good_conditions: Literal["yes", "no",
                                              "inconclusive"] = "no"
    measurements_should_be_running: bool = False
    enclosure_plc_readings: PlcState = PlcState()
    os_state: _OSStateDict = _OSStateDict()

    @staticmethod
    def load() -> PyraCoreState:
        """Load the state from the file system. Possibly raises
        FileNotFoundError, json.JSONDecodeError, AssertionError, or
        ValidationError."""

        with open(_STATE_FILE_PATH, "r") as f:
            current_object = json.load(f)
            assert isinstance(current_object, dict)
            return PyraCoreState(**current_object)

    def dump(self) -> None:
        """Dump the persistent state to the file system."""

        with open(_STATE_FILE_PATH, "w") as f:
            json.dump(self.model_dump(), f, indent=4)


class PyraCoreStatePersistent(pydantic.BaseModel):
    """A pydantic model for the persistent state file."""

    active_opus_macro_id: int = -1
    current_exceptions: list[str] = []

    @staticmethod
    def load() -> PyraCoreStatePersistent:
        """Load the persistent state from the file system. Possibly raises
        FileNotFoundError, json.JSONDecodeError, AssertionError, or
        ValidationError."""

        with open(_PERSISTENT_STATE_FILE_PATH, "r") as f:
            current_object = json.load(f)
            assert isinstance(current_object, dict)
            return PyraCoreStatePersistent(**current_object)

    def dump(self) -> None:
        """Dump the persistent state to the file system."""

        with open(_PERSISTENT_STATE_FILE_PATH, "w") as f:
            json.dump(self.model_dump(), f, indent=4)
