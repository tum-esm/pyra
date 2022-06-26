from packages.core.utils import ConfigInterface
from packages.core.modules.enclosure_control import EnclosureControl


def test_enclosure_control():

    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    plc_state = zip(
        [
            "fan_speed",
            "current_angle",
            "manual control",
            "manual_temp_mode",
            "humidity",
            "temperature",
            "camera",
            "computer",
            "cover_closed",
            "heater",
            "motor_failed",
            "rain",
            "reset_needed",
            "router",
            "spectrometer",
            "ups_alert",
        ],
        control.read_states_from_plc(),
    )
    print(plc_state)

    # control.auto_set_power_spectrometer()

    assert False
