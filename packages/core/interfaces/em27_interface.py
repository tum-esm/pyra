import re
from typing import Optional
import tum_esm_utils
import requests


class EM27Interface:
    """Communicate with the EM27 directly via the HTML interface"""

    @staticmethod
    def get_peak_position(ip: tum_esm_utils.validators.StrictIPv4Adress) -> Optional[int]:
        """Get the peak position of the EM27.

        This reads the ABP value from the EM27 via http://{ip}/config/servmenuA.htm"""
        body = (
            requests.get(f"http://{ip.root}/config/servmenuA.htm")
            .text.replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
            .lower()
        )
        r = re.findall(r'<inputname="abp"value="(\d+)"', body)
        if len(r) != 1:
            return None
        return int(r[0])

    @staticmethod
    def set_peak_position(ip: tum_esm_utils.validators.StrictIPv4Adress) -> Optional[int]:
        """Set the peak position of the EM27.

        It is equivalent to setting the ABP via http://{ip}/config/servmenuA.htm"""
        # TODO
        pass
