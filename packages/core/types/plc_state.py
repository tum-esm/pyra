from typing import Optional, TypedDict


class _PlcStateDictActors(TypedDict):
    fan_speed: Optional[int]
    current_angle: Optional[int]


class _PlcStateDictActorsPartial(TypedDict, total=False):
    camera: Optional[bool]
    fan_speed: Optional[int]
    current_angle: Optional[int]


class _PlcStateDictControl(TypedDict):
    auto_temp_mode: Optional[bool]
    manual_control: Optional[bool]
    manual_temp_mode: Optional[bool]
    sync_to_tracker: Optional[bool]


class _PlcStateDictControlPartial(TypedDict, total=False):
    camera: Optional[bool]
    auto_temp_mode: Optional[bool]
    manual_control: Optional[bool]
    manual_temp_mode: Optional[bool]
    sync_to_tracker: Optional[bool]


class _PlcStateDictSensors(TypedDict):
    humidity: Optional[int]
    temperature: Optional[int]


class _PlcStateDictSensorsPartial(TypedDict, total=False):
    camera: Optional[bool]
    humidity: Optional[int]
    temperature: Optional[int]


class _PlcStateDictState(TypedDict):
    cover_closed: Optional[bool]
    motor_failed: Optional[bool]
    rain: Optional[bool]
    reset_needed: Optional[bool]
    ups_alert: Optional[bool]


class _PlcStateDictStatePartial(TypedDict, total=False):
    camera: Optional[bool]
    cover_closed: Optional[bool]
    motor_failed: Optional[bool]
    rain: Optional[bool]
    reset_needed: Optional[bool]
    ups_alert: Optional[bool]


class _PlcStateDictPower(TypedDict):
    camera: Optional[bool]
    computer: Optional[bool]
    heater: Optional[bool]
    router: Optional[bool]
    spectrometer: Optional[bool]


class _PlcStateDictPowerPartial(TypedDict, total=False):
    camera: Optional[bool]
    computer: Optional[bool]
    heater: Optional[bool]
    router: Optional[bool]
    spectrometer: Optional[bool]


class _PlcStateDictConnections(TypedDict):
    camera: Optional[bool]
    computer: Optional[bool]
    heater: Optional[bool]
    router: Optional[bool]
    spectrometer: Optional[bool]


class _PlcStateDictConnectionsPartial(TypedDict, total=False):
    camera: Optional[bool]
    computer: Optional[bool]
    heater: Optional[bool]
    router: Optional[bool]
    spectrometer: Optional[bool]


class PlcStateDict(TypedDict):
    actors: _PlcStateDictActors
    control: _PlcStateDictControl
    sensors: _PlcStateDictSensors
    state: _PlcStateDictState
    power: _PlcStateDictPower
    connections: _PlcStateDictConnections


class PlcStateDictPartial(TypedDict, total=False):
    actors: _PlcStateDictActorsPartial
    control: _PlcStateDictControlPartial
    sensors: _PlcStateDictSensorsPartial
    state: _PlcStateDictStatePartial
    power: _PlcStateDictPowerPartial
    connections: _PlcStateDictConnectionsPartial
