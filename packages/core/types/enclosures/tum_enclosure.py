from typing import Literal, Optional
import datetime
import pydantic


class StricterBaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", validate_assignment=True)


class StrictIPAdress(pydantic.RootModel[str]):
    root: str = pydantic.Field(..., pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?")


# --- CONFIG ---


class TUMEnclosureConfig(StricterBaseModel):
    ip: StrictIPAdress
    version: Literal[1, 2]
    controlled_by_user: bool


class PartialTUMEnclosureConfig(StricterBaseModel):
    """Like `TUMEnclosureConfig`, but all fields are optional."""

    ip: Optional[StrictIPAdress] = None
    version: Optional[Literal[1, 2]] = None
    controlled_by_user: Optional[bool] = None


# --- STATE ---


class ActorsState(StricterBaseModel):
    fan_speed: Optional[int] = None
    current_angle: Optional[int] = None


class ControlState(StricterBaseModel):
    auto_temp_mode: Optional[bool] = None
    manual_control: Optional[bool] = None
    manual_temp_mode: Optional[bool] = None
    sync_to_tracker: Optional[bool] = None


class SensorsState(StricterBaseModel):
    humidity: Optional[int] = None
    temperature: Optional[int] = None


class StateState(StricterBaseModel):
    cover_closed: Optional[bool] = None
    motor_failed: Optional[bool] = None
    rain: Optional[bool] = None
    reset_needed: Optional[bool] = None
    ups_alert: Optional[bool] = None


class PowerState(StricterBaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class ConnectionsState(StricterBaseModel):
    camera: Optional[bool] = None
    computer: Optional[bool] = None
    heater: Optional[bool] = None
    router: Optional[bool] = None
    spectrometer: Optional[bool] = None


class TUMEnclosureState(StricterBaseModel):
    last_full_fetch: Optional[datetime.datetime] = None
    actors: ActorsState = ActorsState()
    control: ControlState = ControlState()
    sensors: SensorsState = SensorsState()
    state: StateState = StateState()
    power: PowerState = PowerState()
    connections: ConnectionsState = ConnectionsState()
