from typing import Optional
import datetime

from tum_esm_utils.validators import StricterBaseModel, StrictIPv4Adress

# --- CONFIG ---

# TODO: add the config options you need


class AEMETEnclosureConfig(StricterBaseModel):
    ip: StrictIPv4Adress


class PartialAEMETEnclosureConfig(StricterBaseModel):
    """Like `AEMETEnclosureConfig`, but all fields are optional."""

    ip: Optional[StrictIPv4Adress] = None


# --- STATE ---

# TODO: add the state variables you need


class ActorsState(StricterBaseModel):
    fan_speed: Optional[float] = None
    cover_position: Optional[float] = None


class SensorsState(StricterBaseModel):
    humidity: Optional[float] = None
    temperature: Optional[float] = None
    wind_direction: Optional[float] = None
    wind_speed: Optional[float] = None


class AEMETEnclosureState(StricterBaseModel):
    last_full_fetch: Optional[datetime.datetime] = None
    actors: ActorsState = ActorsState()
    sensors: SensorsState = SensorsState()
