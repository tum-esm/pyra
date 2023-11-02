from typing import Literal, Optional
import datetime
import pydantic


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


class StateObject(pydantic.BaseModel):
    last_updated: datetime.datetime
    helios_indicates_good_conditions: Optional[Literal["yes", "no",
                                                       "inconclusive"]] = None
    position: Position = Position()
    measurements_should_be_running: Optional[bool] = None
    plc_state: PLCState = PLCState()
    operating_system_state: OperatingSystemState = OperatingSystemState()
    current_exceptions: Optional[list[str]] = []
    upload_is_running: Optional[bool] = None

    model_config = pydantic.ConfigDict(extra="forbid")
