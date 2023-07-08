from __future__ import annotations
import json
import os
import pydantic
from typing import Optional

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_PERSISTENT_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "logs", "persistent-state.json")


class PersistentState(pydantic.BaseModel):
    """A pydantic model for the persistent state file."""

    active_opus_macro_id: int = -1
    current_exceptions: list[str] = []

    @staticmethod
    def load() -> PersistentState:
        """Load the persistent state from the file system. Possibly raises
        FileNotFoundError, json.JSONDecodeError, AssertionError, or
        ValidationError."""

        with open(_PERSISTENT_STATE_FILE_PATH, "r") as f:
            current_object = json.load(f)
            assert isinstance(current_object, dict)
            return PersistentState(**current_object)

    def dump(self) -> None:
        """Dump the persistent state to the file system."""

        with open(_PERSISTENT_STATE_FILE_PATH, "w") as f:
            json.dump(self.model_dump(), f, indent=4)


class PersistentStatePartial(pydantic.BaseModel):
    """A pydantic model for the persistent state file."""

    active_opus_macro_id: Optional[int] = None
    current_exceptions: Optional[list[str]] = None
