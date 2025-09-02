from __future__ import annotations

import contextlib
import datetime
import os
import pydantic
import tum_esm_utils.sqlitelock
from typing import Generator

from packages.core import types, utils

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "logs", "state.json")

# shared lock file based on SQLite
STATE_LOCK_PATH = os.path.join(_PROJECT_DIR, "logs", "state.sqlitelock")
STATE_LOCK_TIMEOUT = 20
STATE_LOCK_POLL_INTERVAL = 0.2


class StateInterface:
    @staticmethod
    def load_state(
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> types.StateObject:
        """Load the state from the state file."""

        with state_lock:
            return StateInterface._load_state_without_lock(logger)

    @staticmethod
    def _load_state_without_lock(
        logger: utils.Logger,
    ) -> types.StateObject:
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
    def update_state(
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> Generator[types.StateObject, None, None]:
        """Update the state file in a context manager.

        Example:

        ```python
        with interfaces.StateInterface.update_state(logger) as state:
            state.helios_indicates_good_conditions = "yes"
        ```

        The file will be locked correctly, so that no other process can
        interfere with the state file and the state
        """

        with state_lock:
            state = StateInterface._load_state_without_lock(logger)
            state_before = state.model_copy(deep=True)

            yield state

            if state != state_before:
                state.last_updated = datetime.datetime.now()
                with open(_STATE_FILE_PATH, "w") as f:
                    f.write(state.model_dump_json(indent=4))
