from typing import Optional, TypedDict

# TODO: use tuples (3 ints vs 4 ints)


class _PlcSpecificationDictActors(TypedDict):
    current_angle: list[int]
    fan_speed: list[int]
    move_cover: list[int]
    nominal_angle: list[int]


class _PlcSpecificationDictControl(TypedDict):
    auto_temp_mode: list[int]
    manual_control: list[int]
    manual_temp_mode: list[int]
    reset: list[int]
    sync_to_tracker: list[int]


class _PlcSpecificationDictSensors(TypedDict):
    humidity: list[int]
    temperature: list[int]


class _PlcSpecificationDictState(TypedDict):
    cover_closed: list[int]
    motor_failed: Optional[list[int]]
    rain: list[int]
    reset_needed: list[int]
    ups_alert: list[int]


class _PlcSpecificationDictPower(TypedDict):
    camera: list[int]
    computer: Optional[list[int]]
    heater: list[int]
    router: Optional[list[int]]
    spectrometer: list[int]


class _PlcSpecificationDictConnections(TypedDict):
    camera: Optional[list[int]]
    computer: list[int]
    heater: list[int]
    router: list[int]
    spectrometer: Optional[list[int]]


class PlcSpecificationDict(TypedDict):
    actors: _PlcSpecificationDictActors
    control: _PlcSpecificationDictControl
    sensors: _PlcSpecificationDictSensors
    state: _PlcSpecificationDictState
    power: _PlcSpecificationDictPower
    connections: _PlcSpecificationDictConnections
