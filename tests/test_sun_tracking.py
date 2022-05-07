

from packages.core.main import load_config
from packages.core.modules.sun_tracking import SunTracking

def test_ct_measurement():
    _SETUP, _PARAMS = load_config()
    instance = SunTracking(_SETUP, _PARAMS)
    # print(control.continuous_readings())
    # assert(False)

    instance.test_setup()

    assert False