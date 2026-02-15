import pytest
import tum_esm_utils
from packages.core import interfaces, types, utils


@pytest.mark.order(3)
@pytest.mark.integration
def test_tum_enclosure_connection() -> None:
    config = types.Config.load()
    logger = utils.Logger(origin="tum-enclosure", lock=None, just_print=True)
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )

    if config.tum_enclosure is None:
        pytest.skip("TUM Enclosure is not configured")
    else:
        enclosure_interface = interfaces.TUMEnclosureInterface(
            config.tum_enclosure.version,
            config.tum_enclosure.ip,
            state_lock=state_lock,
            logger=logger,
        )
        enclosure_interface.connect()
        enclosure_interface.read()
        enclosure_interface.disconnect()
