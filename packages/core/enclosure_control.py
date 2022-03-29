# Description

import logging

logger = logging.getLogger("pyra.core")


class EnclosureControl:
    def __init__(self):
        self._SETUP = {}
        self._PARAMS = {}

    @staticmethod
    def run():
        if self._SETUP["enclosure_presence"] == 0:
            return

        logger.info("Running EnclosureControl")
        pass

    @property
    def set_config(self):
        pass

    @set_config.setter
    def set_config(self, vals):
        self._SETUP, self._PARAMS = vals