from packages.core.utils import ConfigInterface, OSInfo
from packages.core.modules.enclosure_control import EnclosureControl
import time


def test_enclosure_control():
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)
    print(control.continuous_readings())
    assert False


def test_em27_power_relay():
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)

    state = control.plc_read_bool(_CONFIG["tum_plc"]["power"]["spectrometer"])

    if state == True:
        control.plc_write_bool(_CONFIG["tum_plc"]["power"]["spectrometer"], False)

    time.sleep(2)

    assert not control.plc_read_bool(_CONFIG["tum_plc"]["power"]["spectrometer"])
    assert OSInfo.check_connection_status(_CONFIG["tum_plc"]["ip"]) == "NO_INFO"

    time.sleep(2)

    control.plc_write_bool(_CONFIG["tum_plc"]["power"]["spectrometer"], True)

    time.sleep(10)

    assert control.plc_read_bool(_CONFIG["tum_plc"]["power"]["spectrometer"])
    assert OSInfo.check_connection_status(_CONFIG["tum_plc"]["ip"]) != "NO_INFO"


def test_cover_movement():
    _CONFIG = ConfigInterface().read()
    control = EnclosureControl(_CONFIG)

    control.plc_write_bool(_CONFIG["tum_plc"]["control"]["sync_to_tracker"], False)

    control.plc_write_int(_CONFIG["tum_plc"]["actors"]["move_cover"], 90)
    time.sleep(5)
    assert not control.plc_read_bool(["tum_plc"]["state"]["cover_closed"])
    assert control.plc_read_int(_CONFIG["tum_plc"]["actors"]["move_cover"]) == 90

    control.plc_write_int(_CONFIG["tum_plc"]["actors"]["move_cover"], 250)
    time.sleep(5)
    assert not control.plc_read_bool(["tum_plc"]["state"]["cover_closed"])
    assert control.plc_read_int(_CONFIG["tum_plc"]["actors"]["move_cover"]) == 90

    control.plc_write_int(_CONFIG["tum_plc"]["actors"]["move_cover"], 160)
    time.sleep(5)
    assert not control.plc_read_bool(["tum_plc"]["state"]["cover_closed"])
    assert control.plc_read_int(_CONFIG["tum_plc"]["actors"]["move_cover"]) == 90

    control.plc_write_int(_CONFIG["tum_plc"]["actors"]["move_cover"], 0)
    control.wait_for_cover_closing()
    assert control.plc_read_bool(_CONFIG["tum_plc"]["state"]["cover_closed"])
