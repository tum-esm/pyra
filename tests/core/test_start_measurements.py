from packages.core.utils import ConfigInterface
from packages.core.modules.enclosure_control import EnclosureControl
from packages.core.modules.sun_tracking import SunTracking
from packages.core.modules.opus_measurement import OpusMeasurement

import time


def test_start_measurements():
    _CONFIG = ConfigInterface().read()
    enclosure = EnclosureControl(_CONFIG)
    opus = OpusMeasurement(_CONFIG)
    tracking = SunTracking(_CONFIG)

    if enclosure.plc_state.state.reset_needed:
        enclosure.plc_interface.reset()

    enclosure.plc_interface.set_sync_to_tracker(True)
    time.sleep(2)
    if not tracking.ct_application_running():
        tracking.start_sun_tracking_automation()
        time.sleep(2)
    if not opus.opus_application_running():
        opus.start_opus()
        time.sleep(2)
    opus.load_experiment()
    time.sleep(2)
    opus.start_macro()
