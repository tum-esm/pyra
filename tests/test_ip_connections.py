from packages.core.utils import ConfigInterface, OSInfo


def test_ip_connections():
    _CONFIG = ConfigInterface().read()

    plc_status = OSInfo.check_connection_status(_CONFIG["tum_plc"]["ip"])
    print(plc_status)
    assert  plc_status != 'NO_INFO'
    em27_status = OSInfo.check_connection_status(_CONFIG["opus"]["em27_ip"])
    print(em27_status)
    assert em27_status != 'NO_INFO'

    
