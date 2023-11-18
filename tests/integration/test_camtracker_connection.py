import pytest
from packages.core import types, modules


@pytest.mark.integration
def test_camtracker_connection() -> None:
    config = types.Config.load()
    modules.sun_tracking.SunTracking(config).test_setup()
