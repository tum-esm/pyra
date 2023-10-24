from typing import Optional
import pydantic


class PLCSpecificationActors(pydantic.BaseModel):
    current_angle: tuple[int, int, int]
    fan_speed: tuple[int, int, int]
    move_cover: tuple[int, int, int]
    nominal_angle: tuple[int, int, int]


class PLCSpecificationControl(pydantic.BaseModel):
    auto_temp_mode: tuple[int, int, int, int]
    manual_control: tuple[int, int, int, int]
    manual_temp_mode: tuple[int, int, int, int]
    reset: tuple[int, int, int, int]
    sync_to_tracker: tuple[int, int, int, int]


class PLCSpecificationSensors(pydantic.BaseModel):
    humidity: tuple[int, int, int]
    temperature: tuple[int, int, int]


class PLCSpecificationState(pydantic.BaseModel):
    cover_closed: tuple[int, int, int, int]
    motor_failed: Optional[tuple[int, int, int, int]]
    rain: tuple[int, int, int, int]
    reset_needed: tuple[int, int, int, int]
    ups_alert: tuple[int, int, int, int]


class PLCSpecificationPower(pydantic.BaseModel):
    camera: tuple[int, int, int, int]
    computer: Optional[tuple[int, int, int, int]]
    heater: tuple[int, int, int, int]
    router: Optional[tuple[int, int, int, int]]
    spectrometer: tuple[int, int, int, int]


class PLCSpecificationConnections(pydantic.BaseModel):
    camera: Optional[tuple[int, int, int, int]]
    computer: tuple[int, int, int, int]
    heater: tuple[int, int, int, int]
    router: tuple[int, int, int, int]
    spectrometer: Optional[tuple[int, int, int, int]]


class PLCSpecification(pydantic.BaseModel):
    actors: PLCSpecificationActors
    control: PLCSpecificationControl
    sensors: PLCSpecificationSensors
    state: PLCSpecificationState
    power: PLCSpecificationPower
    connections: PLCSpecificationConnections
