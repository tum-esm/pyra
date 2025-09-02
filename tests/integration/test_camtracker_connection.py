import threading
import pytest
import tum_esm_utils
from packages.core import interfaces, types, threads, utils


@pytest.mark.order(3)
@pytest.mark.integration
def test_camtracker_connection() -> None:
    config = types.Config.load()
    logger = utils.Logger(origin="camtracker", lock=None, just_print=True)
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )
    try:
        threads.camtracker_thread.CamTrackerThread.test_setup(config, state_lock, logger)
    finally:
        threads.camtracker_thread.CamTrackerProgram.stop(config, logger)
