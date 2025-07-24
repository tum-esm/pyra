import datetime
from tum_esm_utils.validators import StrictIPv4Adress
from packages.core import types, utils


class COCCONSpainEnclosureInterface:
    """TODO"""

    @staticmethod
    class DataloggerError(BaseException):
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

    def read(self) -> types.coccon_spain_enclosure.COCCONSpainEnclosureState:
        """Read the whole state of the datalogger."""

        try:
            # TODO

            return types.tum_enclosure.TUMEnclosureState(
                last_full_fetch=datetime.datetime.now(),
                actors=types.coccon_spain_enclosure.ActorsState(
                    fan_speed=None,
                    current_angle=None,
                ),
                sensors=types.coccon_spain_enclosure.SensorsState(
                    humidity=None,
                    temperature=None,
                    wind_direction=None,
                    wind_speed=None,
                ),
            )
        except Exception as e:
            raise COCCONSpainEnclosureInterface.DataloggerError() from e
