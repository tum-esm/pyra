from packages.core import interfaces, modules


def test_opus_connection():
    config = interfaces.ConfigInterface.read()
    modules.opus_measurement.OpusMeasurement(config).test_setup()
