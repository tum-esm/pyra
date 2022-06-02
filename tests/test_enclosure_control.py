
from packages.core.main import load_config
from packages.core.modules.enclosure_control import EnclosureControl
from packages.core.utils.os_info import OSInfo
import time

def test_enclosure_control():
    _SETUP, _PARAMS = load_config()
    control = EnclosureControl(_SETUP, _PARAMS)
    print(control.continuous_readings())
    assert(False)


def test_em27_power_relay():
    _SETUP, _PARAMS = load_config()
    control = EnclosureControl(_SETUP, _PARAMS)

    state = control.plc_read_bool(_SETUP["tum_plc"]["power"]["spectrometer"])

    if state == True:
        control._SETUP["tum_plc"]["power"]["spectrometer"], False

    time.sleep(2)

    assert(control.plc_read_bool(_SETUP["tum_plc"]["power"]["spectrometer"]) == False)
    assert(OSInfo.check_connection_status(_SETUP["tum_plc"]["ip"]) == '"NO_INFO"')

    time.sleep(2)

    control._SETUP["tum_plc"]["power"]["spectrometer"], True

    time.sleep(10)

    assert (control.plc_read_bool(_SETUP["tum_plc"]["power"]["spectrometer"]) == True)
    assert (OSInfo.check_connection_status(_SETUP["tum_plc"]["ip"]) != '"NO_INFO"')




