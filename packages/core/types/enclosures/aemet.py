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

    use_em27_power_plug: bool
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

    use_em27_power_plug: Optional[bool] = None
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
        validation_alias=pydantic.AliasChoices("BattV", "battery_voltage"),
        description="Battery voltage in volts.",
    )
    logger_panel_temperature: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("PTemp_C", "logger_panel_temperature"),
        description="Temperature of the logger panel in degrees celsius.",
    )
    auto_mode: Optional[int] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("AUTO_", "auto_mode"),
        description="Enclosure mode. auto if the enclosure is in automatic mode, manual if it is in manual mode.",
    )
    enhanced_security_mode: Optional[int] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("ENHANCED_SECURITY", "enhanced_security_mode"),
        description="Whether the enhanced security mode is active. 0 if not, 1 if it is active.",
    )
    datalogger_software_version: Optional[str] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices(
            "DATALOGGER_SOFTWARE_VERSION", "datalogger_software_version"
        ),
        description="Software version of the datalogger.",
        examples=["158", "159"],
    )

    # weather sensor readings
    air_pressure_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Press_Int", "air_pressure_internal"),
        description="Internal pressure in hPa.",
    )
    air_pressure_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Press_Ext", "air_pressure_external"),
        description="External pressure in hPa.",
    )
    relative_humidity_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("RH_Int", "relative_humidity_internal"),
        description="Internal relative humidity in percentage.",
    )
    relative_humidity_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("RH_Ext", "relative_humidity_external"),
        description="External relative humidity in percentage.",
    )
    air_temperature_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("AirTC_Int", "air_temperature_internal"),
        description="Internal air temperature in degrees celsius.",
    )
    air_temperature_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("AirTC_Ext", "air_temperature_external"),
        description="External air temperature in degrees celsius.",
    )
    dew_point_temperature_internal: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Trocio_Int", "dew_point_temperature_internal"),
        description="Internal dew point temperature in degrees celsius.",
    )
    dew_point_temperature_external: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Trocio_Ext", "dew_point_temperature_external"),
        description="External dew point temperature in degrees celsius.",
    )
    wind_direction: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Wdir", "wind_direction"),
        description="Wind direction in degrees.",
    )
    wind_velocity: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Wvel", "wind_velocity"),
        description="Wind velocity in m/s.",
    )
    rain_sensor_counter_1: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("LLUVIA_1_In", "rain_sensor_counter_1"),
        description="Rain sensor counter 1. Negative values indicate no rain, positive values indicate rain. The higher the counter the more/longer it has been raining.",
    )
    rain_sensor_counter_2: Optional[float] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("LLUVIA_2_In", "rain_sensor_counter_2"),
        description="Rain sensor counter 2. Negative values indicate no rain, positive values indicate rain. The higher the counter the more/longer it has been raining.",
    )

    # closing reasons
    closed_due_to_rain: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Cerrar_Lluvia", "closed_due_to_rain"),
        description="Whether the cover has been closed due to rain. 0 if not, 1 if it has been closed due to rain.",
    )
    closed_due_to_external_relative_humidity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices(
            "Cerrar_RH_Ext", "closed_due_to_external_relative_humidity"
        ),
        description="Whether the cover has been closed due to high external relative humidity. 0 if not, 1 if it has been closed due to high external relative humidity.",
    )
    closed_due_to_external_air_temperature: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices(
            "Cerrar_AirTC_Ext", "closed_due_to_external_air_temperature"
        ),
        description="Whether the cover has been closed due to high external air temperature. 0 if   not, 1 if it has been closed due to high external air temperature.",
    )
    closed_due_to_internal_relative_humidity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices(
            "Cerrar_RH_Int", "closed_due_to_internal_relative_humidity"
        ),
        description="Whether the cover has been closed due to high internal relative humidity. 0 if not, 1 if it has been closed due to high internal relative humidity.",
    )
    closed_due_to_internal_air_temperature: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices(
            "Cerrar_AirTC_Int", "closed_due_to_internal_air_temperature"
        ),
        description="Whether the cover has been closed due to high internal air temperature. 0 if not, 1 if it has been closed due to high internal air temperature.",
    )
    closed_due_to_wind_velocity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Cerrar_Wvel_Alta", "closed_due_to_wind_velocity"),
        description="Whether the cover has been closed due to high wind velocity. 0 if not, 1 if it has been closed due to high wind velocity.",
    )
    opened_due_to_elevated_internal_humidity: Optional[bool] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices(
            "Abrir_RH_Int_Elevado", "opened_due_to_elevated_internal_humidity"
        ),
        description="Whether the cover has been opened due to elevated internal relative humidity. 0 if not, 1 if it has been opened due to elevated internal relative humidity.",
    )

    # cover states
    alert_level: Optional[Literal[0, 1, 2]] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("ALERTA", "alert_level"),
        description="Alert level. 0 if no alert, 1 if counting towards closing, 2 if should be closed due to alert.",
    )
    averia_fault_code: Optional[int] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("AVERIA", "averia_fault_code"),
        description="Value of AVERIA.",
    )
    cover_status: Optional[Literal["AF", "A.", "A", "C.", "CF", "C"]] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("Estado_actual", "cover_status"),
        description="Current cover status. AF: opening (releasing fechillo), A.: opening, A: open, C.: closing, CF: closing (fechillo), C: closed.",
    )
    motor_position: Optional[int | str] = pydantic.Field(
        default=None,
        validation_alias=pydantic.AliasChoices("posicion", "motor_position"),
        description="Current motor position. 0 is fully open, higher values are more closed.",
    )

    # other
    em27_has_power: Optional[bool] = pydantic.Field(
        default=None,
        description="Whether the EM27 power plug is currently powered on (i.e. whether the EM27 has power). This value does not come from the datalogger, but from the wifi power interruptor.",
    )
    em27_voltage: Optional[float] = pydantic.Field(
        default=None,
        description="Voltage of the EM27 in volts. This value does not come from the datalogger, but from the wifi power interruptor.",
    )
    em27_current: Optional[float] = pydantic.Field(
        default=None,
        description="Current of the EM27 in amps. This value does not come from the datalogger, but from the wifi power interruptor.",
    )
    em27_power: Optional[float] = pydantic.Field(
        default=None,
        description="Power consumption of the EM27 in watts. This value does not come from the datalogger, but from the wifi power interruptor.",
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
