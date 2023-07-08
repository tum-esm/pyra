from typing import Optional
import pydantic


class _PlcStateActors(pydantic.BaseModel):
    fan_speed: Optional[int] = None
    current_angle: Optional[int] = None


class _PlcStateControl(pydantic.BaseModel):
    auto_temp_mode: Optional[bool] = None
    manual_control: Optional[bool] = None
    manual_temp_mode: Optional[bool] = None
    sync_to_tracker: Optional[bool] = None


class _PlcStateSensors(pydantic.BaseModel):
    humidity: Optional[int] = None
    temperature: Optional[int] = None


class _PlcStateState(pydantic.BaseModel):
    cover_closed: Optional[bool] = None
    motor_failed: Optional[bool] = None
    rain: Optional[bool] = None
    reset_needed: Optional[bool] = None
    ups_alert: Optional[bool] = None


class _PlcStatePower(pydantic.BaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class _PlcStateConnections(pydantic.BaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class PlcState(pydantic.BaseModel):
    last_read_time: Optional[str] = None
    actors: _PlcStateActors = _PlcStateActors()
    control: _PlcStateControl = _PlcStateControl()
    sensors: _PlcStateSensors = _PlcStateSensors()
    state: _PlcStateState = _PlcStateState()
    power: _PlcStatePower = _PlcStatePower()
    connections: _PlcStateConnections = _PlcStateConnections()
