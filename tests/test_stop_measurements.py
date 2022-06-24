from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl
from packages.core.modules.sun_tracking import SunTracking
from packages.core.modules.opus_measurement import OpusMeasurement

import time


def test_start_up():
    
    _CONFIG = ConfigInterface().read()
    enclosure = EnclosureControl(_CONFIG)
    opus = OpusMeasurement(_CONFIG)
    tracking = SunTracking(_CONFIG)
    
    enclosure.set_sync_to_tracker(False)
    enclosure.move_cover(0)
    enclosure.wait_for_cover_closing()

    time.sleep(2)
    if tracking.ct_application_running:
        tracking.stop_sun_tracking_automation()
        time.sleep(2)
    if opus.opus_application_running:
        opus.stop_macro()
       
    