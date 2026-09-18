import datetime
from typing import Literal, Optional

import pydantic
from tum_esm_utils.validators import StricterBaseModel

from .enclosures.tum import TUMEnclosureState
from .enclosures.aemet import AEMETEnclosureState

# --- SUBSTATES ---


class ExceptionStateItem(StricterBaseModel):
    origin: str
    exception_type: str
    subject: str
    description: str
    traceback: Optional[str] = None
    details: Optional[str] = None
    raised_at: float
    notified_at: Optional[float] = None
    cleared_at: Optional[float] = None


class Position(StricterBaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    sun_elevation: Optional[float] = None


class OperatingSystemState(StricterBaseModel):
    cpu_usage: Optional[list[float]] = None
    memory_usage: Optional[float] = None
    last_boot_time: Optional[str] = None
    filled_disk_space_fraction: Optional[float] = None


class OpusState(StricterBaseModel):
    experiment_filepath: Optional[str] = None
    macro_filepath: Optional[str] = None
    macro_id: Optional[int] = None
    last_http_connection_issue_time: Optional[float] = None


class ExceptionsState(StricterBaseModel):
    exceptions: list[ExceptionStateItem] = pydantic.Field(
        default=[], description="Exceptions awaiting notification or cleanup."
    )
    notification_sent: bool = pydantic.Field(
        default=False,
        description="Whether an exception notification was sent since this list became nonempty.",
    )


class ActivityState(StricterBaseModel):
    cli_calls: int = 0
    camtracker_startups: int = 0
    opus_startups: int = 0
    upload_is_running: bool = False
    # has_errors, is_measuring can be inferred from the other state fields


# --- STATE ---


class StateObject(StricterBaseModel):
    last_updated: datetime.datetime
    helios_indicates_good_conditions: Optional[Literal["yes", "no", "inconclusive"]] = None
    position: Position = Position()
    measurements_should_be_running: Optional[bool] = None
    last_bad_weather_detection: Optional[float] = None
    tum_enclosure_state: TUMEnclosureState = TUMEnclosureState()
    aemet_enclosure_state: AEMETEnclosureState = AEMETEnclosureState()
    operating_system_state: OperatingSystemState = OperatingSystemState()
    exceptions_state: ExceptionsState = ExceptionsState()
    opus_state: OpusState = OpusState()
    activity: ActivityState = ActivityState()

    model_config = pydantic.ConfigDict(extra="forbid")

    def reset(self) -> None:
        """Reset the state object to its initial values but keep the exceptions."""
        self.helios_indicates_good_conditions = None
        self.position = Position()
        self.measurements_should_be_running = None
        self.last_bad_weather_detection = None
        self.tum_enclosure_state = TUMEnclosureState()
        self.aemet_enclosure_state = AEMETEnclosureState()
        self.operating_system_state = OperatingSystemState()
        self.activity = ActivityState()
