from typing import Optional, TypedDict

import pydantic

# TODO: use tuples instead of lists


class _PlcSpecificationActors(pydantic.BaseModel):
    current_angle: list[int]
    fan_speed: list[int]
    move_cover: list[int]
    nominal_angle: list[int]


class _PlcSpecificationControl(pydantic.BaseModel):
    auto_temp_mode: list[int]
    manual_control: list[int]
    manual_temp_mode: list[int]
    reset: list[int]
    sync_to_tracker: list[int]


class _PlcSpecificationSensors(pydantic.BaseModel):
    humidity: list[int]
    temperature: list[int]


class _PlcSpecificationState(pydantic.BaseModel):
    cover_closed: list[int]
    motor_failed: Optional[list[int]]
    rain: list[int]
    reset_needed: list[int]
    ups_alert: list[int]


class _PlcSpecificationPower(pydantic.BaseModel):
    camera: list[int]
    computer: Optional[list[int]]
    heater: list[int]
    router: Optional[list[int]]
    spectrometer: list[int]


class _PlcSpecificationConnections(pydantic.BaseModel):
    camera: Optional[list[int]]
    computer: list[int]
    heater: list[int]
    router: list[int]
    spectrometer: Optional[list[int]]


class PlcSpecification(pydantic.BaseModel):
    actors: _PlcSpecificationActors
    control: _PlcSpecificationControl
    sensors: _PlcSpecificationSensors
    state: _PlcSpecificationState
    power: _PlcSpecificationPower
    connections: _PlcSpecificationConnections
