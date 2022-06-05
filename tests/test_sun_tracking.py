from packages.core.utils import ConfigInterface
from packages.core.modules.sun_tracking import SunTracking


def test_ct_measurement():
    _CONFIG = ConfigInterface().read()
    instance = SunTracking(_CONFIG)
    # print(control.continuous_readings())
    # assert(False)

    instance.test_setup()

    assert False
