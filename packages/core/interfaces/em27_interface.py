from typing import Optional
import tum_esm_utils


class EM27Interface:
    """Communicate with the EM27 directly via the HTML interface"""

    @staticmethod
    def get_peak_position(ip: tum_esm_utils.validators.StrictIPv4Adress) -> Optional[int]:
        """Get the peak position of the EM27.

        This reads the ABP value from the EM27 via http://{ip}/config/servmenuA.htm"""
        # TODO
        pass

    @staticmethod
    def set_peak_position(ip: tum_esm_utils.validators.StrictIPv4Adress) -> Optional[int]:
        """Set the peak position of the EM27.

        It is equivalent to setting the ABP via http://{ip}/config/servmenuA.htm"""
        # TODO
        pass
