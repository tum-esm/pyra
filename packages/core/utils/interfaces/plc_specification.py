from typing import Literal
from .. import types


# TODO: use tuples (3 ints vs 4 ints)

# these are the pins used on the TUM-PLC for all functionality
PLC_SPECIFICATION_VERSIONS: dict[Literal[1, 2], types.PlcSpecificationDict] = {
    1: {
        "actors": {
            "current_angle": [25, 6, 2],
            "fan_speed": [8, 18, 2],
            "move_cover": [25, 8, 2],
            "nominal_angle": [25, 8, 2],
        },
        "control": {
            "auto_temp_mode": [8, 24, 1, 2],
            "manual_control": [8, 24, 1, 5],
            "manual_temp_mode": [8, 24, 1, 3],
            "reset": [3, 4, 1, 5],
            "sync_to_tracker": [8, 16, 1, 0],
        },
        "sensors": {"humidity": [8, 22, 2], "temperature": [8, 20, 2]},
        "state": {
            "cover_closed": [25, 2, 1, 2],
            "motor_failed": [8, 12, 1, 3],
            "rain": [8, 6, 1, 0],
            "reset_needed": [3, 2, 1, 2],
            "ups_alert": [8, 0, 1, 1],
        },
        "power": {
            "camera": [8, 16, 1, 2],
            "computer": [8, 16, 1, 6],
            "heater": [8, 16, 1, 5],
            "router": [8, 16, 1, 3],
            "spectrometer": [8, 16, 1, 1],
        },
        "connections": {
            "camera": [8, 14, 1, 6],
            "computer": [8, 14, 1, 3],
            "heater": [8, 14, 1, 1],
            "router": [8, 14, 1, 2],
            "spectrometer": [8, 14, 1, 0],
        },
    },
    2: {
        "actors": {
            "current_angle": [6, 6, 2],
            "fan_speed": [8, 4, 2],
            "move_cover": [6, 8, 2],
            "nominal_angle": [6, 8, 2],
        },
        "control": {
            "auto_temp_mode": [8, 24, 1, 5],
            "manual_control": [8, 12, 1, 7],
            "manual_temp_mode": [8, 24, 1, 4],
            "reset": [3, 4, 1, 5],
            "sync_to_tracker": [8, 8, 1, 1],
        },
        "sensors": {"humidity": [8, 22, 2], "temperature": [8, 16, 2]},
        "state": {
            "cover_closed": [6, 16, 1, 1],
            "motor_failed": None,
            "rain": [3, 0, 1, 0],
            "reset_needed": [3, 2, 1, 2],
            "ups_alert": [8, 13, 1, 6],
        },
        "power": {
            "camera": [8, 8, 1, 4],  # K5 Relay
            "computer": None,
            "heater": [8, 12, 1, 7],  # K3 Relay
            "router": None,  # not allowed
            "spectrometer": [8, 8, 1, 2],  # K4 Relay
        },
        "connections": {
            "camera": None,
            "computer": [8, 13, 1, 2],
            "heater": [8, 6, 1, 1],
            "router": [8, 12, 1, 4],
            "spectrometer": None,
        },
    },
}
