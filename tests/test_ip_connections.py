from packages.core.utils import ConfigInterface, OSInfo


def test_ip_connections():
    _CONFIG = ConfigInterface().read()

    assert OSInfo.check_connection_status(_CONFIG["tum_plc"]["ip"]) != '"NO_INFO"'
    assert OSInfo.check_connection_status(_CONFIG["opus"]["em27_ip"]) != '"NO_INFO"'

    assert False
