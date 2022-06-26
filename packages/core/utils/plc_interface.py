from dataclasses import dataclass


@dataclass
class PLCActorsInterface:
    current_angle: list[int]
    fan_speed: list[int]
    move_cover: list[int]
    nominal_angle: list[int]


@dataclass
class PLCControlInterface:
    auto_temp_mode: list[int]
    manual_control: list[int]
    manual_temp_mode: list[int]
    reset: list[int]
    sync_to_tracker: list[int]


@dataclass
class PLCSensorsInterface:
    humidity: list[int]
    temperature: list[int]


@dataclass
class PLCStateInterface:
    cover_closed: list[int]
    motor_failed: list[int]
    rain: list[int]
    reset_needed: list[int]
    ups_alert: list[int]


@dataclass
class PLCPowerInterface:
    camera: list[int]
    computer: list[int]
    heater: list[int]
    router: list[int]
    spectrometer: list[int]


@dataclass
class PLCConnectionsInterface:
    camera: list[int]
    computer: list[int]
    heater: list[int]
    router: list[int]
    spectrometer: list[int]


@dataclass
class PLCInterface:
    actors: PLCActorsInterface
    control: PLCControlInterface
    sensors: PLCSensorsInterface
    state: PLCStateInterface
    power: PLCPowerInterface
    connections: PLCConnectionsInterface


# TODO: Add correct variables for PLC


STANDARD_PLC_INTERFACES: dict[int, PLCInterface] = {
    1: PLCInterface(
        actors=PLCActorsInterface(
            current_angle=[25, 6, 2],
            fan_speed=[8, 18, 2],
            move_cover=[25, 8, 2],
            nominal_angle=[25, 8, 2],
        ),
        control=PLCControlInterface(
            auto_temp_mode=[8, 24, 1, 2],
            manual_control=[8, 24, 1, 5],
            manual_temp_mode=[8, 24, 1, 3],
            reset=[3, 4, 1, 5],
            sync_to_tracker=[8, 16, 1, 0],
        ),
        sensors=PLCSensorsInterface(humidity=[8, 22, 2], temperature=[8, 20, 2]),
        state=PLCStateInterface(
            cover_closed=[25, 2, 1, 2],
            motor_failed=[8, 12, 1, 3],
            rain=[8, 6, 1, 0],
            reset_needed=[3, 2, 1, 2],
            ups_alert=[8, 0, 1, 1],
        ),
        power=PLCPowerInterface(
            camera=[8, 16, 1, 2],
            computer=[8, 16, 1, 6],
            heater=[8, 16, 1, 5],
            router=[8, 16, 1, 3],
            spectrometer=[8, 16, 1, 1],
        ),
        connections=PLCConnectionsInterface(
            camera=[8, 14, 1, 6],
            computer=[8, 14, 1, 3],
            heater=[8, 14, 1, 1],
            router=[8, 14, 1, 2],
            spectrometer=[8, 14, 1, 0],
        ),
    ),
    2: PLCInterface(
        actors=PLCActorsInterface(
            current_angle=[25, 6, 2],
            fan_speed=[8, 18, 2],
            move_cover=[25, 8, 2],
            nominal_angle=[25, 8, 2],
        ),
        control=PLCControlInterface(
            auto_temp_mode=[8, 24, 1, 2],
            manual_control=[8, 24, 1, 5],
            manual_temp_mode=[8, 24, 1, 3],
            reset=[3, 4, 1, 5],
            sync_to_tracker=[8, 16, 1, 0],
        ),
        sensors=PLCSensorsInterface(humidity=[8, 22, 2], temperature=[8, 20, 2]),
        state=PLCStateInterface(
            cover_closed=[25, 2, 1, 2],
            motor_failed=[8, 12, 1, 3],
            rain=[8, 6, 1, 0],
            reset_needed=[3, 2, 1, 2],
            ups_alert=[8, 0, 1, 1],
        ),
        power=PLCPowerInterface(
            camera=[8, 16, 1, 2],
            computer=[8, 16, 1, 6],
            heater=[8, 16, 1, 5],
            router=[8, 16, 1, 3],
            spectrometer=[8, 16, 1, 1],
        ),
        connections=PLCConnectionsInterface(
            camera=[8, 14, 1, 6],
            computer=[8, 14, 1, 3],
            heater=[8, 14, 1, 1],
            router=[8, 14, 1, 2],
            spectrometer=[8, 14, 1, 0],
        ),
    ),
}
