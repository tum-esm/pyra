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
    

    control.sync_to_tracker(True)
    time.sleep(2)
    if not tracking.ct_application_running:
        tracking.start_sun_tracking_automation()
        time.sleep(2)
    if not opus.opus_application_running:
        opus.start_opus()
        time.sleep(2)
    opus.load_experiment()
    time.sleep(2)
    opus.start_macro()

    assert(False)
