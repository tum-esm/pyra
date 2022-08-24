from packages.core import interfaces, modules


def test_opus_connection():
    config = interfaces.ConfigInterface.read()
    modules.sun_tracking.SunTracking(config).test_setup()
