from packages.core.utils import ConfigInterface, OSInfo
from packages.core.modules.sun_tracking import SunTracking
import time


def test_ct_measurement():
    _CONFIG = ConfigInterface().read()
    instance = SunTracking(_CONFIG)
    # print(control.continuous_readings())
    # assert(False)

    ct_path = self._CONFIG["camtracker"]["executable_path"]
    process_name = os.path.basename(ct_path)
    
    status = OSInfo.check_process_status(process_name)

    print(status)


    assert False
