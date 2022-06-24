from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl

import time


def test_cover_movement():
    _CONFIG = ConfigInterface().read()
    _PLC_INTERFACE: PLCInterface = STANDARD_PLC_INTERFACES[_CONFIG["tum_plc"]["version"]]
    control = EnclosureControl(_CONFIG)

    #reset needed? prin
   # reset_needed = control.plc_read_bool(_PLC_INTERFACE.state["reset_needed"])
    #continuous_readings = control.read_state_from_plc()

    #print(f"reset_needed = {reset_needed}, continuous_readings={continuous_readings}")       

    control.plc_write_bool(_PLC_INTERFACE.control["manual_control"], False)
    time.sleep(2)
    control.plc_write_bool(_PLC_INTERFACE.control["sync_to_tracker"], True)
    time.sleep(2)

    #control.plc_write_int(_PLC_INTERFACE.actors["move_cover"], 90)
    #time.sleep(10)
    #control.plc_write_int(_PLC_INTERFACE.actors["move_cover"], 0)
    
    #assert control.plc_read_bool(_PLC_INTERFACE.state["cover_closed"])

    #assert False