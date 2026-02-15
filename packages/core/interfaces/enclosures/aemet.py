from typing import Any, Literal
import requests
import requests.auth
import urllib.parse

import tum_esm_utils
from packages.core import utils, types, interfaces


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
        self.latest_read_state: types.aemet.AEMETEnclosureState = types.aemet.AEMETEnclosureState(
            em27_has_power=True
        )

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

    def read(
        self,
        immediate_write_to_central_state: bool = True,
    ) -> types.aemet.AEMETEnclosureState:
        try:
            out = self._run_command("DataQuery", mode="most-recent", uri="dl:Public")
            headers = [d["name"] for d in out["head"]["fields"]]
            assert len(out["data"]) == 1
            d = dict(zip(headers, out["data"][0]["vals"]))
            d["time"] = out["data"][0]["time"]
            d["no"] = out["data"][0]["no"]
            news = types.aemet.AEMETEnclosureState.model_validate(d)
            news.em27_has_power = self.latest_read_state.em27_has_power
            self.latest_read_state = news
            if immediate_write_to_central_state:
                with interfaces.StateInterface.update_state(self.state_lock, self.logger) as s:
                    s.aemet_enclosure_state = news
            return news
        except Exception as e:
            raise AEMETEnclosureInterface.DataloggerError() from e

    def set_enhanced_security_mode(self, mode: bool) -> None:
        self.logger.info(f"Setting enhanced security mode to {mode}")
        self._set_value("dl:Public.ENHANCED_SECURITY", 1 if mode else 0)
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().enhanced_security_mode == mode,
            timeout_seconds=40,
            timeout_message="Enhanced security mode did not update within 30 seconds.",
            check_interval_seconds=5,
        )

    def set_enclosure_mode(self, mode: Literal["auto", "manual"]) -> None:
        self.logger.info(f"Setting enclosure mode to {mode}")
        if mode == "auto":
            self._set_value("dl:Public.AUTO_", 1)
        else:
            self._set_value("dl:Public.AUTO_", 0)
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().auto_mode == (1 if mode == "auto" else 0),
            timeout_seconds=40,
            timeout_message="Enclosure mode did not update within 30 seconds.",
            check_interval_seconds=5,
        )

    def set_averia_fault_code(self, new_value: int) -> None:
        """Set the averia fault code to the given value, and wait until the datalogger state reflects this change."""
        self.logger.info(f"Setting averia fault code to {new_value}")
        self._set_value("dl:Public.AVERIA", new_value)
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().averia_fault_code == new_value,
            timeout_seconds=40,
            timeout_message="Averia fault code did not update within 30 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info("Averia fault code updated successfully")

    def set_alert_level(self, new_value: int) -> None:
        """Set the alert level to the given value, and wait until the datalogger state reflects this change."""
        self.logger.info(f"Setting alert level to {new_value}")
        self._set_value("dl:Public.ALERTA", new_value)
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: self.read().alert_level == new_value,
            timeout_seconds=40,
            timeout_message="Alert level did not update within 30 seconds.",
            check_interval_seconds=5,
        )
        self.logger.info("Alert level updated successfully")

    def open_cover(self) -> None:
        self.logger.info("Opening cover")
        state = self.read()
        with interfaces.StateInterface.update_state(self.state_lock, self.logger) as s:
            self.latest_read_state.em27_has_power = s.aemet_enclosure_state.em27_has_power
            s.aemet_enclosure_state = state
        if (state.averia_fault_code == 0) and (state.alert_level == 0):
            if state.auto_mode == 1:
                self.set_enclosure_mode("manual")
            self._set_value("dl:Public.MOTOR_ON", 1)
            self._set_value("dl:Public.Estado_actual", "AF")  # open releasing fechillo
            tum_esm_utils.timing.wait_for_condition(
                is_successful=lambda: self.read().pretty_cover_status == "open",
                timeout_seconds=90,
                timeout_message="Cover did not open within 90 seconds.",
                check_interval_seconds=5,
            )

    def close_cover(self) -> None:
        self.logger.info("Closing cover")
        state = self.read()
        if (state.averia_fault_code == 0) and (state.alert_level == 0):
            if state.auto_mode == 1:
                self.set_enclosure_mode("manual")
            self._set_value("dl:Public.MOTOR_ON", 1)
            self._set_value("dl:Public.Estado_actual", "C.")  # closing
            tum_esm_utils.timing.wait_for_condition(
                is_successful=lambda: self.read().pretty_cover_status == "closed",
                timeout_seconds=90,
                timeout_message="Cover did not close within 90 seconds.",
                check_interval_seconds=5,
            )

    def set_em27_power(self, power_on: bool) -> None:
        self.logger.info(f"Turning EM27 power {'on' if power_on else 'off'}")
        self.logger.debug(
            "This is currently not implemented, because the power plugs did not arrive yet."
        )
        with interfaces.StateInterface.update_state(self.state_lock, self.logger) as s:
            s.aemet_enclosure_state.em27_has_power = power_on
            self.latest_read_state.em27_has_power = power_on

        # TODO: communicate with the EM27 power plug
        # TODO: update power state

    def get_em27_power(self) -> bool:
        self.logger.info(f"Fetch the EM27 power state")
        self.logger.debug(
            "This is currently not implemented, because the power plugs did not arrive yet."
        )
        with interfaces.StateInterface.update_state(self.state_lock, self.logger) as s:
            s.aemet_enclosure_state.em27_has_power = True
            self.latest_read_state.em27_has_power = True

        # TODO: communicate with the EM27 power plug
        # TODO: read power state

        return True
