# Description

import logging

logger = logging.getLogger("pyra.core")


class EnclosureControl:
    def __init__(self):
        self._SETUP = {}
        self._PARAMS = {}

    def run(self):
        if not self._SETUP["enclosure_presence"]:
            return

        logger.info("Running EnclosureControl")
        pass

    @property
    def set_config(self):
        pass

    @set_config.setter
    def set_config(self, vals):
        self._SETUP, self._PARAMS = vals


    #check what resetbutton after rain does (and the auto reset option)
    #trigger sync with cover if automation is 1