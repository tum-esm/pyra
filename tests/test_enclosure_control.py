
from packages.core.main import load_config
from packages.core.modules.enclosure_control import EnclosureControl

def test_enclosure_control():
    _SETUP, _PARAMS = load_config()
    control = EnclosureControl(_SETUP, _PARAMS)
    print(control.continuous_readings())
    assert(False)

