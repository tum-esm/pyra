from __future__ import annotations
from typing import Generator
import contextlib
import datetime
import os
import pydantic
import tum_esm_utils
from packages.core import utils, types

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_STATE_LOCK_PATH = os.path.join(_PROJECT_DIR, "logs", ".state.lock")
_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "logs", "state.json")

logger = utils.Logger(origin="state")


class StateInterface:
    @staticmethod
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=5)
    def load_state() -> types.StateObject:
        """Load the state from the state file."""

        return StateInterface._load_state_without_filelock()

    @staticmethod
    def _load_state_without_filelock() -> types.StateObject:
        """Load the state from the state file."""

        try:
            with open(_STATE_FILE_PATH, "r") as f:
                state = types.StateObject.model_validate_json(f.read())
        except (
            FileNotFoundError,
            pydantic.ValidationError,
            UnicodeDecodeError,
        ) as e:
            logger.warning(f"Could not load state file - Creating new one: {e}")
            state = types.StateObject(last_updated=datetime.datetime.now())
            with open(_STATE_FILE_PATH, "w") as f:
                f.write(state.model_dump_json(indent=4))
        return state

    @staticmethod
    @contextlib.contextmanager
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=5)
    def update_state() -> Generator[types.StateObject, None, None]:
        """Update the state file in a context manager.
        
        Example:
        
        ```python
        with interfaces.StateInterface.update_state_in_context() as state:
            state.helios_indicates_good_conditions = "yes"
        ```

        The file will be locked correctly, so that no other process can
        interfere with the state file and the state
        """

        state = StateInterface._load_state_without_filelock()
        state_before = state.model_copy(deep=True)

        yield state

        if state != state_before:
            state.last_updated = datetime.datetime.now()
            with open(_STATE_FILE_PATH, "w") as f:
                f.write(state.model_dump_json(indent=4))
