import datetime
import os
import tum_esm_utils
from packages.core import types

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(
    __file__, current_depth=4
)


class TUMPLCLogger:
    """A class to save the current PLC state to a log file."""
    @staticmethod
    def log(config: types.Config, state: types.StateObject) -> None:
        now = datetime.datetime.now()
        timestamp = now.timestamp()
        datetime_string = now.isoformat()

        log_line = [
            timestamp,
            datetime_string,
            state.position.sun_elevation,
            state.plc_state.power.heater,
            state.plc_state.power.spectrometer,
            state.plc_state.state.rain,
            state.plc_state.actors.fan_speed,
            state.plc_state.actors.current_angle,
            state.plc_state.sensors.temperature,
            state.plc_state.sensors.humidity,
        ]
        stringed_log_line = [
            str(item).lower() if item is not None else "null"
            for item in log_line
        ]
        current_log_file = os.path.join(
            _PROJECT_DIR, "logs", "tum-plc",
            f"{config.general.station_id}-plc-logs-{now.strftime('%Y-%m-%d')}.csv"
        )
        if not os.path.isfile(current_log_file):
            with open(current_log_file, "w") as f:
                f.write(
                    "timestamp,datetime,sun_elevation,heater_power," +
                    "spectrometer_power,rain_detected,fan_speed," +
                    "cover_angle,temperature,humidity\n"
                )
        with open(current_log_file, "a") as f:
            f.write(",".join(stringed_log_line) + "\n")
