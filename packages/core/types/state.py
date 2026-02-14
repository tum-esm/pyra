import datetime
import traceback
from typing import Literal, Optional

import pydantic
from tum_esm_utils.validators import StricterBaseModel

from .enclosures.tum import TUMEnclosureState
from .enclosures.aemet import AEMETEnclosureState

# --- SUBSTATES ---


class ExceptionStateItem(StricterBaseModel):
    origin: str
    subject: str
    details: Optional[str] = None
    send_emails: Optional[bool] = True


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
    current: list[ExceptionStateItem] = pydantic.Field(
        default=[], description="List of exceptions that are currently active."
    )
    notified: list[ExceptionStateItem] = pydantic.Field(
        default=[], description="List of exceptions for which an email was sent out."
    )

    def add_exception_state_item(self, item: ExceptionStateItem) -> None:
        """Add a new exception state item to the state."""

        if item not in self.current:
            self.current.append(item)

    def add_exception(self, origin: str, exception: Exception, send_emails: bool = True) -> None:
        """Add a new exception to the state."""

        self.add_exception_state_item(
            ExceptionStateItem(
                origin=origin,
                subject=type(exception).__name__,
                details="\n".join(traceback.format_exception(exception)),
                send_emails=send_emails,
            )
        )

    def clear_exception_origin(self, origin: str) -> None:
        """Clear all exceptions with the given origin."""

        self.current = [e for e in self.current if e.origin != origin]

    def clear_exception_subject(self, subject: str) -> None:
        """Clear all exceptions with the given subject."""

        self.current = [e for e in self.current if e.subject != subject]

    def has_subject(self, subject: str) -> bool:
        """Check if there is an exception with the given subject."""

        return any(e.subject == subject for e in self.current)


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
    last_rain_detection_time: Optional[float] = None
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
        self.last_rain_detection_time = None
        self.tum_enclosure_state = TUMEnclosureState()
        self.aemet_enclosure_state = AEMETEnclosureState()
        self.operating_system_state = OperatingSystemState()
        self.activity = ActivityState()
