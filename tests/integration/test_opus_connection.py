import pytest
from packages.core import types, modules


@pytest.mark.integration
def test_opus_connection() -> None:
    config = types.Config.load()
    try:
        modules.opus_measurement.OpusMeasurement(config).test_setup()
    finally:
        modules.opus_measurement.OpusMeasurement.force_kill_opus()
