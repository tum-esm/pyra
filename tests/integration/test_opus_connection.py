import pytest
from packages.core import interfaces, modules


@pytest.mark.integration
def test_opus_connection():
    config = interfaces.ConfigInterface.read()
    modules.opus_measurement.OpusMeasurement(config).test_setup()
