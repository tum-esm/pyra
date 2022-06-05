from packages.core.utils import ConfigInterface
from packages.core.modules.enclosure_control import EnclosureControl


def test_enclosure_control():
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    print(control.continuous_readings())
    assert False
