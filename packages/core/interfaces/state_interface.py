from __future__ import annotations
import datetime
import os
from typing import Literal, Optional
import pydantic
import tum_esm_utils
from packages.core import utils, types

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_STATE_LOCK_PATH = os.path.join(_PROJECT_DIR, "logs", ".state.lock")
_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "logs", "state.json")

logger = utils.Logger(origin="state-interface")


class StateObject(pydantic.BaseModel):
    last_updated: datetime.datetime
    helios_indicates_good_conditions: Optional[Literal["yes", "no",
                                                       "inconclusive"]] = None
    measurements_should_be_running: Optional[bool] = None
    plc_state: Optional[types.PLCState] = None
    os_state: Optional[types.OperatingSystemState] = None
    active_opus_macro_id: Optional[int] = None
    current_exceptions: Optional[list[str]] = None


class StateInterface:
    @tum_esm_utils.decorators.with_filelock(
        lockfile_path=_STATE_LOCK_PATH, timeout=5
    )
    @staticmethod
    def load_state() -> StateObject:
        """Load the state from the state file."""
        try:
            with open(_STATE_FILE_PATH, "r") as f:
                state = StateObject.model_validate_json(f.read())
        except (
            FileNotFoundError,
            pydantic.ValidationError,
        ):
            state = StateObject(last_updated=datetime.datetime.now())
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
        enclosure_plc_readings: Optional[dict] = None,
        os_state: Optional[dict] = None,
        active_opus_macro_id: Optional[int] = None,
        current_exceptions: Optional[list[str]] = None,
        enforce_none_values: bool = False,
    ) -> StateObject:
        try:
            with open(_STATE_FILE_PATH, "r") as f:
                state = StateObject.model_validate_json(f.read())
        except FileNotFoundError:
            state = StateObject(
                last_updated=datetime.datetime.now(),
                helios_indicates_good_conditions=None,
                measurements_should_be_running=None,
                enclosure_plc_readings=None,
                os_state=None,
                active_opus_macro_id=None,
                current_exceptions=None
            )

        state.last_updated = datetime.datetime.now()
        if enforce_none_values or (
            helios_indicates_good_conditions is not None
        ):
            state.helios_indicates_good_conditions = helios_indicates_good_conditions
        if enforce_none_values or (measurements_should_be_running is not None):
            state.measurements_should_be_running = measurements_should_be_running
        if enforce_none_values or (enclosure_plc_readings is not None):
            state.enclosure_plc_readings = enclosure_plc_readings
        if enforce_none_values or (os_state is not None):
            state.os_state = os_state
        if enforce_none_values or (active_opus_macro_id is not None):
            state.active_opus_macro_id = active_opus_macro_id
        if enforce_none_values or (current_exceptions is not None):
            state.current_exceptions = current_exceptions

        with open(_STATE_FILE_PATH, "w") as f:
            f.write(state.model_dump_json(indent=4))
