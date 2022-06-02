from packages.core.utils.os_info import OSInfo
from packages.core.main import load_config

def test_ip_connections():
    _SETUP, _PARAMS = load_config()

    assert(OSInfo.check_connection_status(_SETUP["tum_plc"]["ip"]) != '"NO_INFO"')
    assert (OSInfo.check_connection_status(_SETUP["opus"]["em27_ip"]) != '"NO_INFO"')

    assert(False)
