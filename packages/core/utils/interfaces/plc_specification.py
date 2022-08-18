from dataclasses import dataclass
from typing import Literal, Optional


# TODO: use typeddict
# TODO: use tuples (3 ints vs 4 ints)


@dataclass
class PLCActorsSpecification:
    current_angle: list[int]
    fan_speed: list[int]
    move_cover: list[int]
    nominal_angle: list[int]


@dataclass
class PLCControlSpecification:
    auto_temp_mode: list[int]
    manual_control: list[int]
    manual_temp_mode: list[int]
    reset: list[int]
    sync_to_tracker: list[int]


@dataclass
class PLCSensorsSpecification:
    humidity: list[int]
    temperature: list[int]


@dataclass
class PLCStateSpecification:
    cover_closed: list[int]
    motor_failed: Optional[list[int]]
    rain: list[int]
    reset_needed: list[int]
    ups_alert: list[int]


@dataclass
class PLCPowerSpecification:
    camera: list[int]
    computer: Optional[list[int]]
    heater: list[int]
    router: Optional[list[int]]
    spectrometer: list[int]


@dataclass
class PLCConnectionsSpecification:
    camera: Optional[list[int]]
    computer: list[int]
    heater: list[int]
    router: list[int]
    spectrometer: Optional[list[int]]


@dataclass
class PLCSpecification:
    actors: PLCActorsSpecification
    control: PLCControlSpecification
    sensors: PLCSensorsSpecification
    state: PLCStateSpecification
    power: PLCPowerSpecification
    connections: PLCConnectionsSpecification


# these are the pins used on the TUM-PLC for all functionality
PLC_SPECIFICATION_VERSIONS: dict[Literal[1, 2], PLCSpecification] = {
    1: PLCSpecification(
        actors=PLCActorsSpecification(
            current_angle=[25, 6, 2],
            fan_speed=[8, 18, 2],
            move_cover=[25, 8, 2],
            nominal_angle=[25, 8, 2],
        ),
        control=PLCControlSpecification(
            auto_temp_mode=[8, 24, 1, 2],
            manual_control=[8, 24, 1, 5],
            manual_temp_mode=[8, 24, 1, 3],
            reset=[3, 4, 1, 5],
            sync_to_tracker=[8, 16, 1, 0],
        ),
        sensors=PLCSensorsSpecification(humidity=[8, 22, 2], temperature=[8, 20, 2]),
        state=PLCStateSpecification(
            cover_closed=[25, 2, 1, 2],
            motor_failed=[8, 12, 1, 3],
            rain=[8, 6, 1, 0],
            reset_needed=[3, 2, 1, 2],
            ups_alert=[8, 0, 1, 1],
        ),
        power=PLCPowerSpecification(
            camera=[8, 16, 1, 2],
            computer=[8, 16, 1, 6],
            heater=[8, 16, 1, 5],
            router=[8, 16, 1, 3],
            spectrometer=[8, 16, 1, 1],
        ),
        connections=PLCConnectionsSpecification(
            camera=[8, 14, 1, 6],
            computer=[8, 14, 1, 3],
            heater=[8, 14, 1, 1],
            router=[8, 14, 1, 2],
            spectrometer=[8, 14, 1, 0],
        ),
    ),
    2: PLCSpecification(
        actors=PLCActorsSpecification(
            current_angle=[6, 6, 2],
            fan_speed=[8, 4, 2],
            move_cover=[6, 8, 2],
            nominal_angle=[6, 8, 2],
        ),
        control=PLCControlSpecification(
            auto_temp_mode=[8, 24, 1, 5],
            manual_control=[8, 12, 1, 7],
            manual_temp_mode=[8, 24, 1, 4],
            reset=[3, 4, 1, 5],
            sync_to_tracker=[8, 8, 1, 1],
        ),
        sensors=PLCSensorsSpecification(humidity=[8, 22, 2], temperature=[8, 16, 2]),
        state=PLCStateSpecification(
            cover_closed=[6, 16, 1, 1],
            motor_failed=None,
            rain=[3, 0, 1, 0],
            reset_needed=[3, 2, 1, 2],
            ups_alert=[8, 13, 1, 6],
        ),
        power=PLCPowerSpecification(
            camera=[8, 8, 1, 4],  # K5 Relay
            computer=None,
            heater=[8, 12, 1, 7],  # K3 Relay
            router=None,  # not allowed
            spectrometer=[8, 8, 1, 2],  # K4 Relay
        ),
        connections=PLCConnectionsSpecification(
            camera=None,
            computer=[8, 13, 1, 2],
            heater=[8, 6, 1, 1],
            router=[8, 12, 1, 4],
            spectrometer=None,
        ),
    ),
}
