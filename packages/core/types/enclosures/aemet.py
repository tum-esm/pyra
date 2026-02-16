from typing import Literal, Optional
import datetime

import pydantic
from tum_esm_utils.validators import StricterBaseModel, StrictIPv4Adress

# --- CONFIG ---


class AEMETEnclosureConfig(StricterBaseModel):
    datalogger_ip: StrictIPv4Adress
    datalogger_port: int
    datalogger_username: str
    datalogger_password: str

    em27_power_plug_ip: StrictIPv4Adress
    em27_power_plug_port: int
    em27_power_plug_username: str
    em27_power_plug_password: str

    toggle_em27_power: bool
    controlled_by_user: bool


class PartialAEMETEnclosureConfig(StricterBaseModel):
    """Like `AEMETEnclosureConfig`, but all fields are optional."""

    datalogger_ip: Optional[StrictIPv4Adress] = None
    datalogger_port: Optional[int] = None
    datalogger_username: Optional[str] = None
    datalogger_password: Optional[str] = None

    em27_power_plug_ip: Optional[StrictIPv4Adress] = None
    em27_power_plug_port: Optional[int] = None
    em27_power_plug_username: Optional[str] = None
    em27_power_plug_password: Optional[str] = None

    toggle_em27_power: Optional[bool] = None
    controlled_by_user: Optional[bool] = None


# --- STATE ---


class AEMETEnclosureState(pydantic.BaseModel):
    # general
    dt: Optional[datetime.datetime] = pydantic.Field(
        default=None,
        description="Time of this datalogger state.",
    )
    battery_voltage: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="BattV",
        description="Battery voltage in volts.",
    )
    logger_panel_temperature: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="PTemp_C",
        description="Temperature of the logger panel in degrees celsius.",
    )
    auto_mode: Optional[Literal[0, 1]] = pydantic.Field(
        default=None,
        validation_alias="AUTO_",
        description="Enclosure mode. auto if the enclosure is in automatic mode, manual if it is in manual mode.",
    )
    enhanced_security_mode: Optional[Literal[0, 1]] = pydantic.Field(
        default=None,
        validation_alias="ENHANCED_SECURITY",
        description="Whether the enhanced security mode is active. 0 if not, 1 if it is active.",
    )

    # weather sensor readings
    air_pressure_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="Press_Int",
        description="Internal pressure in hPa.",
    )
    air_pressure_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="Press_Ext",
        description="External pressure in hPa.",
    )
    relative_humidity_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="RH_Int",
        description="Internal relative humidity in percentage.",
    )
    relative_humidity_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="RH_Ext",
        description="External relative humidity in percentage.",
    )
    air_temperature_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="AirTC_Int",
        description="Internal air temperature in degrees celsius.",
    )
    air_temperature_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="AirTC_Ext",
        description="External air temperature in degrees celsius.",
    )
    dew_point_temperature_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="Trocio_Int",
        description="Internal dew point temperature in degrees celsius.",
    )
    dew_point_temperature_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="Trocio_Ext",
        description="External dew point temperature in degrees celsius.",
    )
    wind_direction: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="Wdir",
        description="Wind direction in degrees.",
    )
    wind_velocity: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="Wvel",
        description="Wind velocity in m/s.",
    )
    rain_sensor_counter_1: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="LLUVIA_1_In",
        description="Rain sensor counter 1. Negative values indicate no rain, positive values indicate rain. The higher the counter the more/longer it has been raining.",
    )
    rain_sensor_counter_2: Optional[float] = pydantic.Field(
        default=None,
        validation_alias="LLUVIA_2_In",
        description="Rain sensor counter 2. Negative values indicate no rain, positive values indicate rain. The higher the counter the more/longer it has been raining.",
    )

    # closing reasons
    closed_due_to_rain: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Cerrar_Lluvia",
        description="Whether the cover has been closed due to rain. 0 if not, 1 if it has been closed due to rain.",
    )
    closed_due_to_external_relative_humidity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Cerrar_RH_Ext",
        description="Whether the cover has been closed due to high external relative humidity. 0 if not, 1 if it has been closed due to high external relative humidity.",
    )
    closed_due_to_external_air_temperature: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Cerrar_AirTC_Ext",
        description="Whether the cover has been closed due to high external air temperature. 0 if   not, 1 if it has been closed due to high external air temperature.",
    )
    closed_due_to_internal_relative_humidity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Cerrar_RH_Int",
        description="Whether the cover has been closed due to high internal relative humidity. 0 if not, 1 if it has been closed due to high internal relative humidity.",
    )
    closed_due_to_internal_air_temperature: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Cerrar_AirTC_Int",
        description="Whether the cover has been closed due to high internal air temperature. 0 if not, 1 if it has been closed due to high internal air temperature.",
    )
    closed_due_to_wind_velocity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Cerrar_Wvel_Alta",
        description="Whether the cover has been closed due to high wind velocity. 0 if not, 1 if it has been closed due to high wind velocity.",
    )
    opened_due_to_elevated_internal_humidity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias="Abrir_RH_Int_Elevado",
        description="Whether the cover has been opened due to elevated internal relative humidity. 0 if not, 1 if it has been opened due to elevated internal relative humidity.",
    )

    # cover states
    alert_level: Optional[Literal[0, 1, 2]] = pydantic.Field(
        default=None,
        validation_alias="ALERTA",
        description="Alert level. 0 if no alert, 1 if counting towards closing, 2 if should be closed due to alert.",
    )
    averia_fault_code: Optional[int] = pydantic.Field(
        default=None,
        validation_alias="AVERIA",
        description="Value of AVERIA.",
    )
    cover_status: Optional[Literal["AF", "A.", "A", "C.", "CF", "C"]] = pydantic.Field(
        default=None,
        validation_alias="Estado_actual",
        description="Current cover status. AF: opening (releasing fechillo), A.: opening, A: open, C.: closing, CF: closing (fechillo), C: closed.",
    )
    motor_position: Optional[int | str] = pydantic.Field(
        default=None,
        validation_alias="posicion",
        description="Current motor position. 0 is fully open, higher values are more closed.",
    )

    # other
    em27_has_power: Optional[bool] = pydantic.Field(
        default=None,
        description="Whether the EM27 power plug is currently powered on (i.e. whether the EM27 has power). This value does not come from the datalogger, but from the wifi power interruptor.",
    )

    @property
    def pretty_cover_status(
        self,
    ) -> Literal[
        "opening-lock",
        "opening-hood",
        "open",
        "closing-hood",
        "closing-lock",
        "closed",
        "unknown",
    ]:
        if self.cover_status == "AF":
            return "opening-lock"
        elif self.cover_status == "A.":
            return "opening-hood"
        elif self.cover_status == "A":
            return "open"
        elif self.cover_status == "C.":
            return "closing-hood"
        elif self.cover_status == "CF":
            return "closing-lock"
        elif self.cover_status == "C":
            return "closed"
        else:
            return "unknown"

    @property
    def pretty_enclosure_mode(
        self,
    ) -> Literal[
        "auto",
        "manual",
        "unknown",
    ]:
        if self.auto_mode == 1:
            return "auto"
        elif self.auto_mode == 0:
            return "manual"
        else:
            return "unknown"
