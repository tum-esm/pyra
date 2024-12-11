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
        try:
            raw_body = requests.get(f"http://{ip.root}/config/servmenuA.htm", timeout=3)
        except:
            return None
        body = raw_body.text.replace("\n", "").replace("\t", "").replace(" ", "").lower()
        r: list[str] = re.findall(r'<inputname="abp"value="(\d+)"', body)
        if len(r) != 1:
            return None
        return int(r[0])

    @staticmethod
    def set_peak_position(
        ip: tum_esm_utils.validators.StrictIPv4Adress,
        new_peak_position: int,
    ) -> None:
        """Set the peak position of the EM27.

        It is equivalent to setting the ABP via http://{ip}/config/servmenuA.htm"""
        try:
            requests.get(
                f"http://{ip.root}/config/servmenuA.htm?sub=Send^&ABP={new_peak_position}^",
                timeout=3,
            )
        except Exception as e:
            raise RuntimeError(f"Could not set peak position: {e}")

