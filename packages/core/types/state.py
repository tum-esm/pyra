import traceback
from typing import Literal, Optional
import datetime
import pydantic


class ExceptionStateItem(pydantic.BaseModel):
    origin: str
    subject: str
    details: Optional[str] = None
    send_emails: Optional[bool] = True


class Position(pydantic.BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    sun_elevation: Optional[float] = None


class OperatingSystemState(pydantic.BaseModel):
    cpu_usage: Optional[list[float]] = None
    memory_usage: Optional[float] = None
    last_boot_time: Optional[str] = None
    filled_disk_space_fraction: Optional[float] = None


class PLCStateActors(pydantic.BaseModel):
    fan_speed: Optional[int] = None
    current_angle: Optional[int] = None


class PLCStateControl(pydantic.BaseModel):
    auto_temp_mode: Optional[bool] = None
    manual_control: Optional[bool] = None
    manual_temp_mode: Optional[bool] = None
    sync_to_tracker: Optional[bool] = None


class PLCStateSensors(pydantic.BaseModel):
    humidity: Optional[int] = None
    temperature: Optional[int] = None


class PLCStateState(pydantic.BaseModel):
    cover_closed: Optional[bool] = None
    motor_failed: Optional[bool] = None
    rain: Optional[bool] = None
    reset_needed: Optional[bool] = None
    ups_alert: Optional[bool] = None


class PLCStatePower(pydantic.BaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class PLCStateConnections(pydantic.BaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class PLCState(pydantic.BaseModel):
    last_full_fetch: Optional[datetime.datetime] = None
    actors: PLCStateActors = PLCStateActors()
    control: PLCStateControl = PLCStateControl()
    sensors: PLCStateSensors = PLCStateSensors()
    state: PLCStateState = PLCStateState()
    power: PLCStatePower = PLCStatePower()
    connections: PLCStateConnections = PLCStateConnections()

    model_config = pydantic.ConfigDict(extra="forbid")


class OpusState(pydantic.BaseModel):
    experiment_filepath: Optional[str] = None
    macro_filepath: Optional[str] = None
    macro_id: Optional[int] = None


class ExceptionsState(pydantic.BaseModel):
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


class StateObject(pydantic.BaseModel):
    last_updated: datetime.datetime
    recent_cli_calls: int = 0
    helios_indicates_good_conditions: Optional[Literal["yes", "no", "inconclusive"]] = None
    position: Position = Position()
    measurements_should_be_running: Optional[bool] = None
    plc_state: PLCState = PLCState()
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
        self.plc_state = PLCState()
        self.operating_system_state = OperatingSystemState()
        self.upload_is_running = None
