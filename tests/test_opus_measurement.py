

from packages.core.main import load_config
from packages.core.modules.opus_measurement import OpusMeasurement

def test_opus_measurement():
    _SETUP, _PARAMS = load_config()
    instance = OpusMeasurement(_SETUP, _PARAMS)
    # print(control.continuous_readings())
    # assert(False)

    instance.test_setup()

    assert False
