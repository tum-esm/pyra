from packages.core.utils import ConfigInterface
from packages.core.modules.opus_measurement import OpusMeasurement


def test_opus_measurement():
    _CONFIG = ConfigInterface().read()
    instance = OpusMeasurement(_CONFIG)
    # print(control.continuous_readings())
    # assert(False)

    instance.test_setup()

    assert False
