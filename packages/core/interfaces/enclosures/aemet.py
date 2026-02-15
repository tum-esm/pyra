from typing import Any, Literal
import requests
import requests.auth
import urllib.parse
from packages.core import types


class AEMETEnclosureInterface:
    class DataloggerError(Exception):
        """Raised when the datalogger did not respond as expected."""

    def __init__(
        self,
        config: types.aemet.AEMETEnclosureConfig,
    ) -> None:
        self.enclosure_config = config

    def _run_command(self, command: str, **kwargs: Any) -> dict[Any, Any]:
        return requests.get(
            (
                f"http://{self.enclosure_config.datalogger_ip}:{self.enclosure_config.datalogger_port}/csapi/"
                + f"?command={command}&format=json&"
                + urllib.parse.urlencode(kwargs, safe=":")
            ),
            auth=requests.auth.HTTPBasicAuth(
                self.enclosure_config.datalogger_username,
                self.enclosure_config.datalogger_password,
            ),
        ).json()

    def update_config(
        self,
        new_config: types.aemet.AEMETEnclosureConfig,
    ) -> None:
        """Update the internally used config (executed at the)
        beginning of enclosure-control's run-function.

        Reconnecting to Datalogger, when IP has changed."""

        self.enclosure_config = new_config

    def read(self) -> types.aemet.AEMETEnclosureState:
        try:
            out = self._run_command("DataQuery", mode="most-recent", uri="dl:Public")
            headers = [d["name"] for d in out["head"]["fields"]]
            assert len(out["data"]) == 1
            d = dict(zip(headers, out["data"][0]["vals"]))
            d["time"] = out["data"][0]["time"]
            d["no"] = out["data"][0]["no"]
            return types.aemet.AEMETEnclosureState.model_validate(d)
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError() from e

    def _set_value(self, uri: str, value: str | int) -> None:
        self._run_command("SetValueEx", uri=uri, value=value)

    def set_enclosure_mode(self, mode: Literal["auto", "manual"]) -> None:
        if mode == "auto":
            self._set_value("dl:Public.AUTO_", 1)
        else:
            self._set_value("dl:Public.AUTO_", 0)

    def open_cover(self) -> None:
        state = self.read()
        if (state.averia_fault_code == 0) and (state.alert_level == 0):
            self.set_enclosure_mode("manual")
            self._set_value("dl:Public.MOTOR_ON", 1)
            self._set_value("dl:Public.Estado_actual", "AF")  # open releasing fechillo

    def cover_close(self) -> None:
        state = self.read()
        if (state.averia_fault_code == 0) and (state.alert_level == 0):
            self._set_value("dl:Public.AUTO_", 0)  # manual
            self._set_value("dl:Public.MOTOR_ON", 1)
            self._set_value("dl:Public.Estado_actual", "C.")  # closing
