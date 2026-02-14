import datetime
from tum_esm_utils.validators import StrictIPv4Adress
from packages.core import types, utils


class AEMETEnclosureInterface:
    """TODO"""

    class DataloggerError(Exception):
        """Raised when the datalogger did not respond as expected."""

    def __init__(
        self,
        datalogger_ip: StrictIPv4Adress,
        logger: utils.Logger,
    ) -> None:
        self.datalogger_ip = datalogger_ip.root
        self.logger = logger

    def update_config(self, new_datalogger_ip: StrictIPv4Adress) -> None:
        """Update the internally used config (executed at the)
        beginning of enclosure-control's run-function.

        Reconnecting to Datalogger, when IP has changed."""

        if self.datalogger_ip != new_datalogger_ip.root:
            self.logger.debug("Datalogger ip has changed, reconnecting now")
            # TODO: possibly reconnect to datalogger

        # TODO: you might not need this if you only do HTTP requests

    # BULK READ

    def read(self) -> types.aemet.AEMETEnclosureState:
        """Read the whole state of the datalogger."""

        try:
            # TODO

            return types.aemet.AEMETEnclosureState(
                last_full_fetch=datetime.datetime.now(),
                actors=types.aemet.ActorsState(
                    fan_speed=None,
                    cover_position=None,
                ),
                sensors=types.aemet.SensorsState(
                    humidity=None,
                    temperature=None,
                    wind_direction=None,
                    wind_speed=None,
                ),
            )
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError() from e
