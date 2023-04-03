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
    """TypeDict:

    ```ts
    {
        last_read_time: string | null,
        actors: {
            fan_speed: number | null,
            current_angle: number | null
        },
        control: {
            auto_temp_mode: boolean | null,
            manual_control: boolean | null,
            manual_temp_mode: boolean | null,
            sync_to_tracker: boolean | null
        },
        sensors: {
            humidity: number | null,
            temperature: number | null
        },
        state: {
            cover_closed: boolean | null,
            motor_failed: boolean | null,
            rain: boolean | null,
            reset_needed: boolean | null,
            ups_alert: boolean | null
        },
        power: {
            camera: boolean | null,
            computer: boolean | null,
            heater: boolean | null,
            router: boolean | null,
            spectrometer: boolean | null
        },
        connections: {
            camera: boolean | null,
            computer: boolean | null,
            heater: boolean | null,
            router: boolean | null,
            spectrometer: boolean | null
        }
    }
    ```
    """

    last_read_time: Optional[str]
    actors: _PlcStateDictActors
    control: _PlcStateDictControl
    sensors: _PlcStateDictSensors
    state: _PlcStateDictState
    power: _PlcStateDictPower
    connections: _PlcStateDictConnections


class PlcStateDictPartial(TypedDict, total=False):
    """TypedDict: like `PlcStateDict`, but all fields are optional."""

    last_read_time: Optional[str]
    actors: _PlcStateDictActorsPartial
    control: _PlcStateDictControlPartial
    sensors: _PlcStateDictSensorsPartial
    state: _PlcStateDictStatePartial
    power: _PlcStateDictPowerPartial
    connections: _PlcStateDictConnectionsPartial
