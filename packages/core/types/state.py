from typing import Literal, Optional
import traceback
import datetime
import pydantic
from .enclosures import tum_enclosure
from tum_esm_utils.validators import StricterBaseModel

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


class ExceptionsState(StricterBaseModel):
    current: list[ExceptionStateItem] = pydantic.Field(
        [], description="List of exceptions that are currently active."
    )
    notified: list[ExceptionStateItem] = pydantic.Field(
        [], description="List of exceptions for which an email was sent out."
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
                send_emails=send_emails
            )
        )

    def clear_exception_origin(self, origin: str) -> None:
        """Clear all exceptions with the given origin."""

        self.current = [e for e in self.current if e.origin != origin]


# --- STATE ---


class StateObject(StricterBaseModel):
    last_updated: datetime.datetime
    recent_cli_calls: int = 0
    helios_indicates_good_conditions: Optional[Literal["yes", "no", "inconclusive"]] = None
    position: Position = Position()
    measurements_should_be_running: Optional[bool] = None
    tum_enclosure_state: tum_enclosure.TUMEnclosureState = tum_enclosure.TUMEnclosureState()
    operating_system_state: OperatingSystemState = OperatingSystemState()
    exceptions_state: ExceptionsState = ExceptionsState()
    upload_is_running: Optional[bool] = None
    opus_state: OpusState = OpusState()

    model_config = pydantic.ConfigDict(extra="forbid")

    def reset(self) -> None:
        """Reset the state object to its initial values but keep the exceptions."""
        self.recent_cli_calls = 0
        self.helios_indicates_good_conditions = None
        self.position = Position()
        self.measurements_should_be_running = None
        self.tum_enclosure_state = tum_enclosure.TUMEnclosureState()
        self.operating_system_state = OperatingSystemState()
        self.upload_is_running = None
