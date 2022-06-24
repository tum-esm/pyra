from packages.core.utils import ConfigInterface, OSInfo, STANDARD_PLC_INTERFACES, PLCInterface
from packages.core.modules.enclosure_control import EnclosureControl
from packages.core.modules.sun_tracking import SunTracking
from packages.core.modules.opus_measurement import OpusMeasurement

import time


def test_start_up():
    
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    opus = OpusMeasurement(_CONFIG)
    tracking = SunTracking(_CONFIG)
    
    control.set_sync_to_tracker(True)
    time.sleep(2)
    if tracking.ct_application_running:
        tracking.stop_sun_tracking_automation()
        time.sleep(2)
    if opus.opus_application_running:
        opus.stop_macro()
       
    