# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220401
# version           : 3.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# ==============================================================================

import logging

# TODO: Cleanup Imports
import snap7
from snap7 import client as c
from snap7.snap7types import *
from snap7 import util



logger = logging.getLogger("pyra.core")


class EnclosureControl:
    """https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf"""
    def __init__(self):
        self._SETUP = {}
        self._PARAMS = {}
        self.plc = c.Client()
        self.connection = self.plc_connect()

    def run(self):
        if not self._SETUP["enclosure_presence"]:
            return

        # check what resetbutton after rain does (and the auto reset option)
        # trigger sync with cover if automation is 1

        logger.info("Running EnclosureControl")
        pass

    @property
    def set_config(self):
        pass

    @set_config.setter
    def set_config(self, vals):
        self._SETUP, self._PARAMS = vals

    def plc_connect(self):
        """Connects to the PLC Snap7

        Returns:
        True -> connected
        False -> not connected
        """
        self.plc.connect('10.10.0.4', 0, 1)
        return self.plc.get_connected()

    def plc_disconnect(self):
        """Disconnects from the PLC Snap7

        Returns:
        True -> disconnected
        False -> not disconnected
        """
        self.plc.disconnect()

        if not self.plc.get_connected():
            return True
        else:
            return False

    def plc_read_int(self, action):
        """Redas an INT value in the PLC database."""
        assert(len(action) == 3)
        db_number, start, size = action

        msg = self.plc.db_read(db_number, start, size)
        value = util.get_int(msg, 0)
        return value

    def plc_write_int(self, action, value):
        """Changes an INT value in the PLC database."""
        assert (len(action) == 3)
        db_number, start, size = action

        msg = bytearray(size)
        util.set_int(msg, 0, value)
        self.plc.db_write(db_number, start, msg)

    def plc_read_bool(self, action):
        """Reads a BOOL value in the PLC database."""
        assert (len(action) == 4)
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        value = util.get_bool(msg, 0, bool_index)
        return value

    def plc_write_bool(self, action, value):
        """Changes a BOOL value in the PLC database."""
        assert (len(action) == 4)
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        util.set_bool(msg, 0, bool_index, value)
        self.plc.db_write(db_number, start, msg)
