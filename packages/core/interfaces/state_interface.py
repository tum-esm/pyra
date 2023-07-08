from __future__ import annotations
import json
import os
import shutil
from pydantic_core._pydantic_core import ValidationError
import tum_esm_utils
from packages.core import types, utils

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_STATE_LOCK_PATH = os.path.join(_PROJECT_DIR, "config", ".state.lock")
_RUNTIME_DATA_PATH = os.path.join(_PROJECT_DIR, "runtime-data")
logger = utils.Logger(origin="state-interface")


class StateInterface:
    """Use JSON files to communicate state between different parts
    of Pyra Core, and between Core and CLI/UI.

    The `runtime-data/state.json` file will be cleared with every
    restart of PYRA Core. The `logs/persistent-state.json` will only
    be created, when it does not exist yet.

    `runtime-data/state.json`:

    ```json
    {
        "helios_indicates_good_conditions": ...,
        "measurements_should_be_running": ...,
        "enclosure_plc_readings": {...},
        "os_state": {...}
    }
    ```

    `logs/persistent-state.json`:

    ```json
    {
        "active_opus_macro_id": ...,
        "current_exceptions": []
    }
    ```"""

    @staticmethod
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=10)
    def initialize() -> None:
        """Clear `state.json`, create empty `prersistent-state.json` if
        it does not exist yet."""

        # clear runtime-data directory
        if os.path.exists(_RUNTIME_DATA_PATH):
            shutil.rmtree(_RUNTIME_DATA_PATH)
        os.mkdir(_RUNTIME_DATA_PATH)

        # create the state file
        types.State().dump()

        # possibly create the persistent state file
        try:
            types.PersistentState.load()
        except (FileNotFoundError, json.JSONDecodeError, AssertionError, ValidationError):
            types.PersistentState().dump()

    @staticmethod
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=10)
    def read() -> types.State:
        """Read the state file and return its content"""
        return StateInterface.read_without_filelock()

    @staticmethod
    def read_without_filelock() -> types.State:
        """Read the state file and return its content"""
        try:
            return types.State.load()
        except (FileNotFoundError, json.JSONDecodeError, AssertionError, ValidationError):
            logger.warning("reinitializing the corrupted state file")
            new_object = types.State()
            new_object.dump()
            return new_object

    @staticmethod
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=10)
    def read_persistent() -> types.PersistentState:
        """Read the persistent state file and return its content"""
        return StateInterface.read_persistent_without_filelock()

    @staticmethod
    def read_persistent_without_filelock() -> types.PersistentState:
        """Read the persistent state file and return its content"""
        try:
            return types.PersistentState.load()
        except (FileNotFoundError, json.JSONDecodeError, AssertionError, ValidationError):
            logger.warning("reinitializing the corrupted persistent state file")
            new_object = types.PersistentState()
            new_object.dump()
            return new_object

    @staticmethod
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=10)
    def update(update: types.StatePartial) -> None:
        """Update the (persistent) state file and return its content.
        The update object should only include the properties to be
        changed in contrast to containing the whole file."""

        current_state = StateInterface.read_without_filelock()
        if update.helios_indicates_good_conditions is not None:
            current_state.helios_indicates_good_conditions = (
                update.helios_indicates_good_conditions
            )
        if update.measurements_should_be_running is not None:
            current_state.measurements_should_be_running = (
                update.measurements_should_be_running
            )
        if update.enclosure_plc_readings is not None:
            current_state.enclosure_plc_readings = update.enclosure_plc_readings
        if update.os_state is not None:
            current_state.os_state = update.os_state
        current_state.dump()

    @staticmethod
    @tum_esm_utils.decorators.with_filelock(lockfile_path=_STATE_LOCK_PATH, timeout=10)
    def update_persistent(update: types.PersistentStatePartial) -> None:
        """Update the (persistent) state file and return its content.
        The update object should only include the properties to be
        changed in contrast to containing the whole file."""

        current_state = StateInterface.read_persistent_without_filelock()
        if update.active_opus_macro_id is not None:
            current_state.active_opus_macro_id = update.active_opus_macro_id
        if update.current_exceptions is not None:
            current_state.current_exceptions = update.current_exceptions
        current_state.dump()
