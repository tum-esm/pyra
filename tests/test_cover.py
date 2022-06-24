from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl

import time


def test_cover_movement():
    _CONFIG = ConfigInterface().read()
    _PLC_INTERFACE: PLCInterface = STANDARD_PLC_INTERFACES[_CONFIG["tum_plc"]["version"]]
    enclosure = EnclosureControl(_CONFIG)
    
    if enclosure.check_for_reest_needed():
        enclosure.reset()

    enclosure.set_sync_to_tracker(False)

    enclosure.move_cover(120)
    time.sleep(10)
    enclosure.move_cover(0)
    enclosure.wait_for_cover_closing()
