from typing import Optional
import pydantic


class OperatingSystemState(pydantic.BaseModel):
    cpu_usage: Optional[list[float]] = None
    memory_usage: Optional[float] = None
    last_boot_time: Optional[str] = None
    filled_disk_space_fraction: Optional[float] = None


class _PLCStateActors(pydantic.BaseModel):
    fan_speed: Optional[int] = None
    current_angle: Optional[int] = None


class _PLCStateControl(pydantic.BaseModel):
    auto_temp_mode: Optional[bool] = None
    manual_control: Optional[bool] = None
    manual_temp_mode: Optional[bool] = None
    sync_to_tracker: Optional[bool] = None


class _PLCStateSensors(pydantic.BaseModel):
    humidity: Optional[int] = None
    temperature: Optional[int] = None


class _PLCStateState(pydantic.BaseModel):
    cover_closed: Optional[bool] = None
    motor_failed: Optional[bool] = None
    rain: Optional[bool] = None
    reset_needed: Optional[bool] = None
    ups_alert: Optional[bool] = None


class _PLCStatePower(pydantic.BaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class _PLCStateConnections(pydantic.BaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class PLCState(pydantic.BaseModel):
    last_read_time: Optional[str] = None
    actors: _PLCStateActors = _PLCStateActors()
    control: _PLCStateControl = _PLCStateControl()
    sensors: _PLCStateSensors = _PLCStateSensors()
    state: _PLCStateState = _PLCStateState()
    power: _PLCStatePower = _PLCStatePower()
    connections: _PLCStateConnections = _PLCStateConnections()
