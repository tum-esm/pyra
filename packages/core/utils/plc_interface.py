from dataclasses import dataclass


@dataclass
class PLCInterface:
    actors: dict[str, list[int]]
    control: dict[str, list[int]]
    power: dict[str, list[int]]
    sensors: dict[str, list[int]]
    state: dict[str, list[int]]


# TODO: Add correct variables for PLC

STANDARD_PLC_INTERFACES: dict[int, PLCInterface] = {
    1: PLCInterface(
        actors={
            "current_angle": [25, 6, 2],
            "fan_speed": [8, 18, 2],
            "move_cover": [25, 8, 2],
            "nominal_angle": [25, 8, 2],
        },
        control={
            "auto_temp_mode": [8, 24, 1, 2],
            "manual_control": [8, 24, 1, 5],
            "manual_temp_mode": [8, 24, 1, 3],
            "reset": [3, 4, 1, 5],
            "sync_to_tracker": [8, 16, 1, 0],
        },
        power={
            "camera": [8, 16, 1, 2],
            "computer": [8, 16, 1, 6],
            "heater": [8, 16, 1, 5],
            "router": [8, 16, 1, 3],
            "spectrometer": [8, 16, 1, 1],
        },
        sensors={"humidity": [8, 22, 2], "temperature": [8, 20, 2]},
        state={
            "camera": [8, 14, 1, 6],
            "computer": [8, 14, 1, 3],
            "cover_closed": [25, 2, 1, 2],
            "heater": [8, 14, 1, 1],
            "motor_failed": [8, 12, 1, 3],
            "rain": [8, 6, 1, 0],
            "reset_needed": [3, 2, 1, 3],
            "router": [8, 14, 1, 2],
            "spectrometer": [8, 14, 1, 0],
            "ups_alert": [8, 0, 1, 1],
        },
    ),
    2: PLCInterface(
        actors={
            "current_angle": [25, 6, 2],
            "fan_speed": [8, 18, 2],
            "move_cover": [25, 8, 2],
            "nominal_angle": [25, 8, 2],
        },
        control={
            "auto_temp_mode": [8, 24, 1, 2],
            "manual_control": [8, 24, 1, 5],
            "manual_temp_mode": [8, 24, 1, 3],
            "reset": [3, 4, 1, 5],
            "sync_to_tracker": [8, 16, 1, 0],
        },
        power={
            "camera": [8, 16, 1, 2],
            "computer": [8, 16, 1, 6],
            "heater": [8, 16, 1, 5],
            "router": [8, 16, 1, 3],
            "spectrometer": [8, 16, 1, 1],
        },
        sensors={"humidity": [8, 22, 2], "temperature": [8, 20, 2]},
        state={
            "camera": [8, 14, 1, 6],
            "computer": [8, 14, 1, 3],
            "cover_closed": [25, 2, 1, 2],
            "heater": [8, 14, 1, 1],
            "motor_failed": [8, 12, 1, 3],
            "rain": [8, 6, 1, 0],
            "reset_needed": [3, 2, 1, 3],
            "router": [8, 14, 1, 2],
            "spectrometer": [8, 14, 1, 0],
            "ups_alert": [8, 0, 1, 1],
        },
    ),
}