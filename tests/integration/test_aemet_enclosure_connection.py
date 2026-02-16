import time
import pytest
import tum_esm_utils
from packages.core import interfaces, types, utils


@pytest.mark.order(3)
@pytest.mark.integration
def test_aemet_enclosure_connection() -> None:
    config = types.Config.load()
    logger = utils.Logger(origin="aemet-enclosure", lock=None, just_print=True)
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )

    if config.aemet_enclosure is None:
        pytest.skip("AEMET Enclosure is not configured")
    else:
        enclosure_interface = interfaces.AEMETEnclosureInterface(
            config=config.aemet_enclosure,
            state_lock=state_lock,
            logger=logger,
        )
        enclosure_interface.read(immediate_write_to_central_state=False)
        if config.aemet_enclosure.use_em27_power_plug:
            enclosure_interface.set_em27_power(True)
            enclosure_interface.read(immediate_write_to_central_state=False)
            assert enclosure_interface.state.em27_has_power == True
            time.sleep(2)
            enclosure_interface.set_em27_power(False)
            enclosure_interface.read(immediate_write_to_central_state=False)
            assert enclosure_interface.state.em27_has_power == False
            time.sleep(2)
            enclosure_interface.set_em27_power(True)
            enclosure_interface.read(immediate_write_to_central_state=False)
            assert enclosure_interface.state.em27_has_power == True
