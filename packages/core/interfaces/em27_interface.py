import datetime
import re
from typing import Optional
import tum_esm_utils
import requests
from packages.core import utils


class EM27Interface:
    """Communicate with the EM27 directly via the HTML interface"""

    @staticmethod
    def get_peak_position(ip: tum_esm_utils.validators.StrictIPv4Adress) -> Optional[int]:
        """Get the peak position of the EM27.

        This reads the ABP value from the EM27 via http://{ip}/config/servmenuA.htm"""
        body = EM27Interface._get_html(ip, "/config/servmenuA.htm")
        r: list[str] = re.findall(r'<input name="abp" value="(\d+)"', body)
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

    @staticmethod
    def get_last_powerup_timestamp(
        ip: tum_esm_utils.validators.StrictIPv4Adress,
    ) -> Optional[float]:
        """Get the peak position of the EM27.

        This reads the ABP value from the EM27 via http://{ip}/config/cfg_ctrler.htm"""
        body = EM27Interface._get_html(ip, "/config/cfg_ctrler.htm")
        r: list[str] = re.findall(r"<td id=tila>([^<]+)</td>", body)
        if len(r) != 1:
            return None

        dt = utils.parse_verbal_timedelta_string(r[0])
        last_powerup_time = datetime.datetime.now() - dt
        return last_powerup_time.timestamp()

    @staticmethod
    def _get_html(
        ip: tum_esm_utils.validators.StrictIPv4Adress,
        url: str,
    ) -> Optional[float]:
        """Fetches a HTML page from the EM27: http://{ip}{url}"""
        try:
            raw_body = requests.get(f"http://{ip.root}{url}", timeout=3)
        except Exception:
            return None
        body = raw_body.text.replace("\n", " ").replace("\t", " ").lower()
        while "  " in body:
            body = body.replace("  ", " ")
        return body
