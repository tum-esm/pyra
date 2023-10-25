from __future__ import annotations
from typing import Generator, Literal, Optional
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

logger = utils.Logger(origin="state-interface")


class StateInterface:
    @tum_esm_utils.decorators.with_filelock(
        lockfile_path=_STATE_LOCK_PATH, timeout=5
    )
    @staticmethod
    def load_state() -> types.StateObject:
        """Load the state from the state file."""

        try:
            with open(_STATE_FILE_PATH, "r") as f:
                state = types.StateObject.model_validate_json(f.read())
        except (
            FileNotFoundError,
            pydantic.ValidationError,
        ):
            state = types.StateObject(last_updated=datetime.datetime.now())
            with open(_STATE_FILE_PATH, "w") as f:
                f.write(state.model_dump_json(indent=4))
        return state

    @tum_esm_utils.decorators.with_filelock(
        lockfile_path=_STATE_LOCK_PATH, timeout=5
    )
    @staticmethod
    def update_state(
        helios_indicates_good_conditions: Optional[Literal["yes", "no",
                                                           "inconclusive"]
                                                  ] = None,
        measurements_should_be_running: Optional[bool] = None,
        plc_state: Optional[types.PLCState] = None,
        operating_system_state: Optional[types.OperatingSystemState] = None,
        current_exceptions: Optional[list[str]] = None,
        upload_is_running: Optional[bool] = None,
        enforce_none_values: bool = False,
    ) -> None:
        """Update the state file. Values that are not explicitly set will not
        be changed in the state file. Only if `enforce_none_values` is set to
        `True`, all values not explicitly set will be set to `None`."""

        try:
            with open(_STATE_FILE_PATH, "r") as f:
                state = types.StateObject.model_validate_json(f.read())
        except FileNotFoundError:
            state = types.StateObject(last_updated=datetime.datetime.now())

        state.last_updated = datetime.datetime.now()
        if enforce_none_values or (
            helios_indicates_good_conditions is not None
        ):
            state.helios_indicates_good_conditions = helios_indicates_good_conditions
        if enforce_none_values or (measurements_should_be_running is not None):
            state.measurements_should_be_running = measurements_should_be_running
        if enforce_none_values or (plc_state is not None):
            state.plc_state = plc_state or types.PLCState()
        if enforce_none_values or (operating_system_state is not None):
            state.operating_system_state = operating_system_state or types.OperatingSystemState(
            )
        if enforce_none_values or (current_exceptions is not None):
            state.current_exceptions = current_exceptions
        if enforce_none_values or (upload_is_running is not None):
            state.upload_is_running = upload_is_running

        with open(_STATE_FILE_PATH, "w") as f:
            f.write(state.model_dump_json(indent=4))

    @staticmethod
    @contextlib.contextmanager
    @tum_esm_utils.decorators.with_filelock(
        lockfile_path=_STATE_LOCK_PATH, timeout=5
    )
    def update_state_in_context() -> Generator[types.StateObject, None, None]:
        """Update the state file in a context manager.
        
        Example:
        
        ```python
        with interfaces.StateInterface.update_state_in_context() as state:
            state.helios_indicates_good_conditions = "yes"
        ```

        The file will be locked correctly, so that no other process can
        interfere with the state file and the state
        """

        try:
            with open(_STATE_FILE_PATH, "r") as f:
                state = types.StateObject.model_validate_json(f.read())
        except FileNotFoundError:
            state = types.StateObject(last_updated=datetime.datetime.now())

        state.last_updated = datetime.datetime.now()
        yield state

        with open(_STATE_FILE_PATH, "w") as f:
            f.write(state.model_dump_json(indent=4))
