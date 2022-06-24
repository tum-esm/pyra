from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl

import time

def test_cover_movement():
    _CONFIG = ConfigInterface().read()
    _PLC_INTERFACE: PLCInterface = STANDARD_PLC_INTERFACES[_CONFIG["tum_plc"]["version"]]
    enclosure = EnclosureControl(_CONFIG)

    state = enclosure.check_for_rest_needed()
    print(state)

    enclosure.reset()

    state = enclosure.check_for_rest_needed()
    print(state)

    assert(False)