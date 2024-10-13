import pytest
from packages.core import types, threads, utils


@pytest.mark.integration
def test_camtracker_connection() -> None:
    config = types.Config.load()
    logger = utils.Logger(origin="camtracker", just_print=True)
    threads.camtracker_thread.CamTrackerThread.test_setup(config, logger)
