from packages.core.utils import ConfigInterface
from packages.core.modules.enclosure_control import EnclosureControl


def test_enclosure_control():

    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    print(control.read_states_from_plc())

    # control.auto_set_power_spectrometer()

    assert False
