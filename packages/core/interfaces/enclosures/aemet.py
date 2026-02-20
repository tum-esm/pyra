import datetime
import time
from typing import Any, Literal, Optional
import requests
import requests.auth
import urllib.parse

import tum_esm_utils
from packages.core import utils, types, interfaces


class TasmotaPlug:
    def __init__(
        self,
        ip_address: str,
        port: int,
        username: str,
        password: str,
    ):
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password

    def _request(self, command: str) -> dict[Any, Any]:
        auth: Optional[requests.auth.HTTPBasicAuth] = None

        try:
            response = requests.get(
                f"http://{self.ip_address}:{self.port}/cm",
                params={"cmnd": command},
                auth=auth,
                timeout=5,
            )
            response.raise_for_status()
            return response.json()  # type: ignore
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError(
                f"Failed to send command '{command}' to Tasmota plug: {e}"
            ) from e

    def power_on(self) -> None:
        self._request("Power ON")
        time.sleep(1)
        new_state = self.get_power_state()
        if not new_state:
            raise AEMETEnclosureInterface.DataloggerError(
                "Failed to turn on the Tasmota plug - power state did not update."
            )

    def power_off(self) -> None:
        self._request("Power OFF")
        time.sleep(1)
        new_state = self.get_power_state()
        if new_state:
            raise AEMETEnclosureInterface.DataloggerError(
                "Failed to turn off the Tasmota plug - power state did not update."
            )

    def get_power_state(self) -> bool:
        answer = self._request("Power")
        try:
            return answer["POWER"] == "ON"  # type: ignore
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError(
                f"Unexpected response from Tasmota plug when getting power state: {answer}"
            ) from e

    def get_throughput_state(self) -> dict[str, float]:
        answer = self._request("Status 8")
        try:
            energy_data = answer["StatusSNS"]["ENERGY"]
            return {
                "em27_voltage": float(energy_data["Voltage"]),
                "em27_current": float(energy_data["Current"]),
                "em27_power": float(energy_data["Power"]),
            }
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError(
                f"Unexpected response from Tasmota plug when getting energy state: {answer}"
            ) from e


class AEMETEnclosureInterface:
    class DataloggerError(Exception):
        """Raised when the datalogger did not respond as expected."""

    def __init__(
        self,
        config: types.aemet.AEMETEnclosureConfig,
        state_lock: tum_esm_utils.sqlitelock.SQLiteLock,
        logger: utils.Logger,
    ) -> None:
        self.enclosure_config = config
        self.state_lock = state_lock
        self.logger = logger
        self.state: types.aemet.AEMETEnclosureState = types.aemet.AEMETEnclosureState()
        self.tasmota_plug = TasmotaPlug(
            ip_address=config.em27_power_plug_ip.root,
            port=config.em27_power_plug_port,
            username=config.em27_power_plug_username,
            password=config.em27_power_plug_password,
        )

    def _run_command(self, command: str, **kwargs: Any) -> Any:
        return requests.get(
            (
                f"http://{self.enclosure_config.datalogger_ip.root}:{self.enclosure_config.datalogger_port}/csapi/"
                + f"?command={command}&format=json&"
                + urllib.parse.urlencode(kwargs, safe=":")
            ),
            auth=requests.auth.HTTPBasicAuth(
                self.enclosure_config.datalogger_username,
                self.enclosure_config.datalogger_password,
            ),
        ).json()

    def _set_value(self, uri: str, value: str | int) -> None:
        self._run_command("SetValueEx", uri=uri, value=value)

    def update_config(
        self,
        new_config: types.aemet.AEMETEnclosureConfig,
    ) -> None:
        """Update the internally used config (executed at the)
        beginning of enclosure-control's run-function.

        Reconnecting to Datalogger, when IP has changed."""

        self.enclosure_config = new_config
        self.tasmota_plug = TasmotaPlug(
            ip_address=new_config.em27_power_plug_ip.root,
            port=new_config.em27_power_plug_port,
            username=new_config.em27_power_plug_username,
            password=new_config.em27_power_plug_password,
        )

    def read(
        self,
        immediate_write_to_central_state: bool = True,
    ) -> types.aemet.AEMETEnclosureState:
        try:
            out = self._run_command("DataQuery", mode="most-recent", uri="dl:Public")
            headers = [d["name"] for d in out["head"]["fields"]]

            new_state_invalid: bool = False
            news: Optional[types.aemet.AEMETEnclosureState] = None
            if len(out["data"]) == 0:
                new_state_invalid = True
            else:
                d = dict(zip(headers, out["data"][0]["vals"]))
                # d["time"] = out["data"][0]["time"]
                # d["no"] = out["data"][0]["no"]
                news = types.aemet.AEMETEnclosureState.model_validate(d)
                if self.enclosure_config.use_em27_power_plug:
                    news.em27_has_power = self.tasmota_plug.get_power_state()
                    throughput_state = self.tasmota_plug.get_throughput_state()
                    news.em27_voltage = throughput_state["em27_voltage"]
                    news.em27_current = throughput_state["em27_current"]
                    news.em27_power = throughput_state["em27_power"]

                news.dt = datetime.datetime.now(tz=datetime.timezone.utc)
                if news.auto_mode is None:
                    new_state_invalid = True

            if new_state_invalid:
                self.logger.warning("Datalogger returned null data")
                if self.state.dt is None:
                    raise AEMETEnclosureInterface.DataloggerError(
                        "Datalogger returned invalid state, and no previous valid state available."
                    )
                elif self.state.dt < (
                    datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=3)
                ):
                    raise AEMETEnclosureInterface.DataloggerError(
                        "Datalogger returned invalid state, and the latest valid state is older than 3 minutes."
                    )
                else:
                    return self.state
            else:
                assert news is not None  # should not happen
                self.state = news
                if immediate_write_to_central_state:
                    with interfaces.StateInterface.update_state(self.state_lock, self.logger) as s:
                        s.aemet_enclosure_state = news
                return news
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError() from e

    def set_enhanced_security_mode(self, mode: bool) -> None:
        self.logger.info(f"Setting enhanced security mode to {mode}")
        self._set_value("dl:Public.ENHANCED_SECURITY", 1 if mode else 0)
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().enhanced_security_mode == mode,
            timeout_seconds=40,
            timeout_message="Enhanced security mode did not update within 30 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info(f"Successfully set enhanced security mode within {dt:.2f} seconds")

    def set_enclosure_mode(self, mode: Literal["auto", "manual"]) -> None:
        self.logger.info(f"Setting enclosure mode to {mode}")
        if mode == "auto":
            self._set_value("dl:Public.AUTO_", 1)
        else:
            self._set_value("dl:Public.AUTO_", 0)
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().auto_mode == (1 if mode == "auto" else 0),
            timeout_seconds=40,
            timeout_message="Enclosure mode did not update within 30 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info(f"Successfully set enclosure mode within {dt:.2f} seconds")

    def set_averia_fault_code(self, new_value: int) -> None:
        """Set the averia fault code to the given value, and wait until the datalogger state reflects this change."""
        self.logger.info(f"Setting averia fault code to {new_value}")
        self._set_value("dl:Public.AVERIA", new_value)
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().averia_fault_code == new_value,
            timeout_seconds=40,
            timeout_message="Averia fault code did not update within 30 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info("Averia fault code updated successfully")
        self.logger.info(f"Successfully set averia fault code within {dt:.2f} seconds")

    def set_alert_level(self, new_value: int) -> None:
        """Set the alert level to the given value, and wait until the datalogger state reflects this change."""
        self.logger.info(f"Setting alert level to {new_value}")
        self._set_value("dl:Public.ALERTA", new_value)
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().alert_level == new_value,
            timeout_seconds=40,
            timeout_message="Alert level did not update within 30 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info(f"Successfully set alert level within {dt:.2f} seconds")

    def open_cover(self) -> None:
        state = self.read()
        if state.alert_level == 2:
            self.logger.warning("Alert level is 2, Pyra will not attempt to move the cover.")
            return

        if state.averia_fault_code is None:
            self.logger.warning(
                "Averia fault code is null, Pyra will not attempt to move the cover."
            )
            return

        if state.averia_fault_code != 0:
            self.logger.warning(
                f"Averia fault code is {state.averia_fault_code}, not moving cover until it is cleared."
            )
            self.clear_averia_fault(state.averia_fault_code)

        self.logger.info("Opening cover")
        if state.auto_mode == 1:
            self.set_enclosure_mode("manual")
        self._set_value("dl:Public.MOTOR_ON", 1)
        self._set_value("dl:Public.Estado_actual", "AF")  # open releasing fechillo
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().pretty_cover_status == "open",
            timeout_seconds=90,
            timeout_message="Cover did not open within 90 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info(f"Successfully opened cover within {dt:.2f} seconds")

    def close_cover(self) -> None:
        state = self.read()
        if state.alert_level == 2:
            self.logger.warning("Alert level is 2, Pyra will not attempt to move the cover.")
            return

        if state.averia_fault_code is None:
            self.logger.warning(
                "Averia fault code is null, Pyra will not attempt to move the cover."
            )
            return

        if state.averia_fault_code != 0:
            self.logger.warning(
                f"Averia fault code is {state.averia_fault_code}, not moving cover until it is cleared."
            )
            self.clear_averia_fault(state.averia_fault_code)

        self.logger.info("Closing cover")
        if state.auto_mode == 1:
            self.set_enclosure_mode("manual")
        self._set_value("dl:Public.MOTOR_ON", 1)
        self._set_value("dl:Public.Estado_actual", "C.")  # closing
        dt = tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().pretty_cover_status == "closed",
            timeout_seconds=90,
            timeout_message="Cover did not close within 90 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info(f"Successfully closed cover within {dt:.2f} seconds")

    def clear_averia_fault(self, current_averia_code: int) -> None:
        code: Optional[int] = current_averia_code
        self.logger.info(f"Trying to clear averia fault, current code: {code}")
        for i in range(3):
            self.logger.info(f"Clearing averia fault, attempt {i + 1}/3")
            self.set_enclosure_mode("manual")
            self.set_averia_fault_code(0)
            self.logger.info("Waiting 30 seconds to check for averia fault clearance...")
            time.sleep(30)
            code = self.read().averia_fault_code
            if code == 0:
                self.logger.info(
                    f"Averia fault successfully cleared (AVERIA=0) after {i + 1} attempts"
                )
                return
            else:
                self.logger.warning(f"Averia fault code is still {code} after attempt {i + 1}")

        raise AEMETEnclosureInterface.DataloggerError(
            f"Failed to clear averia fault after 3 attempts. Current averia code: {code}"
        )

    def set_em27_power(self, power_on: bool) -> None:
        self.logger.info(f"Turning EM27 power {'on' if power_on else 'off'}")
        if power_on:
            self.tasmota_plug.power_on()
        else:
            self.tasmota_plug.power_off()
        with interfaces.StateInterface.update_state(self.state_lock, self.logger) as s:
            s.aemet_enclosure_state.em27_has_power = power_on
            self.state.em27_has_power = power_on
