from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl
import time


def test_enclosure_control():
    
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    print(["fan_speed","current_angle","manual control","manual_temp_mode",
           "humidity", "temperature", "camera", "computer", "cover_closed",
           "heater", "motor_failed", "rain", "reset_needed", "router",
           "spectrometer","ups_alert"])
    print(control.read_states_from_plc())

    control.auto_set_power_spectrometer()

    assert(False)