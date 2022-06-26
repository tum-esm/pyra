from packages.core.utils import ConfigInterface, OSInfo
from packages.core.modules.sun_tracking import SunTracking
import time


def test_ct_measurement():
    _CONFIG = ConfigInterface().read()
    instance = SunTracking(_CONFIG)
    # print(control.continuous_readings())
    # assert(False)

    process_name =
    status = OSInfo.check_process_status(process_name)


    assert False
