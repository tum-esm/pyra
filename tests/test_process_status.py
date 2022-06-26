from packages.core.utils import ConfigInterface
from packages.core.modules.sun_tracking import SunTracking
import time


def test_ct_measurement():
    _CONFIG = ConfigInterface().read()
    instance = SunTracking(_CONFIG)
    # print(control.continuous_readings())
    # assert(False)

    for _ in range(5):
        print(instance.ct_application_running())
        time.sleep(2)

    assert False
