from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl
import time


def test_enclosure_control():
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    control.set_power_camera(False)
    time.sleep(45)
    control.set_power_camera(True)
