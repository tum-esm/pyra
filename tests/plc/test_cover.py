from packages.core.utils import ConfigInterface
from packages.core.modules.enclosure_control import EnclosureControl

import time


def test_cover_movement():
    _CONFIG = ConfigInterface().read()
    enclosure = EnclosureControl(_CONFIG)

    if enclosure.plc_state.state.reset_needed:
        enclosure.plc_interface.reset()

    # assert not enclosure.check_for_reset_needed()

    # enclosure.set_sync_to_tracker(False)

    # enclosure.move_cover(120)
    # time.sleep(10)
    enclosure.move_cover(0)
    enclosure.wait_for_cover_closing()
