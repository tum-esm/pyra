from packages.core.utils import ConfigInterface
from packages.core.modules.sun_tracking import SunTracking


def test_ct_measurement():
    _CONFIG = ConfigInterface().read()
    instance = SunTracking(_CONFIG)
    # print(control.continuous_readings())
    # assert(False)

    log_line = instance.read_ct_log_learn_az_elev()

    print(log_line)

    instance.valdiate_tracker_position()

    assert False
