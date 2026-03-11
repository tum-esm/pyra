import datetime
import os
from typing import Any

import tum_esm_utils

from packages.core import types

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)


class TUMEnclosureLogger:
    """A class to save the current TUM Enclosure state to a log file."""

    @staticmethod
    def log(config: types.Config, state: types.StateObject) -> None:
        now = datetime.datetime.now()
        timestamp = now.timestamp()
        datetime_string = now.isoformat()

        log_line: list[Any] = [
            timestamp,
            datetime_string,
            state.position.sun_elevation,
            state.tum_enclosure_state.power.heater,
            state.tum_enclosure_state.power.spectrometer,
            state.tum_enclosure_state.state.rain,
            state.tum_enclosure_state.actors.fan_speed,
            state.tum_enclosure_state.actors.current_angle,
            state.tum_enclosure_state.sensors.temperature,
            state.tum_enclosure_state.sensors.humidity,
        ]
        stringed_log_line = [str(item).lower() if item is not None else "null" for item in log_line]
        current_log_file = os.path.join(
            _PROJECT_DIR,
            "logs",
            "tum-enclosure",
            f"{config.general.station_id}-tum-enclosure-logs-{now.strftime('%Y-%m-%d')}.csv",
        )
        if not os.path.isfile(current_log_file):
            with open(current_log_file, "w") as f:
                f.write(
                    ",".join(
                        [
                            "timestamp",
                            "datetime",
                            "sun_elevation",
                            "heater_power",
                            "spectrometer_power",
                            "rain_detected",
                            "fan_speed",
                            "cover_angle",
                            "temperature",
                            "humidity",
                        ]
                    )
                    + "\n"
                )
        with open(current_log_file, "a") as f:
            f.write(",".join(stringed_log_line) + "\n")


class AEMETEnclosureLogger:
    """A class to save the current AEMET Enclosure state to a log file."""

    @staticmethod
    def log(config: types.Config, state: types.StateObject) -> None:
        now = datetime.datetime.now()
        timestamp = now.timestamp()
        datetime_string = now.isoformat()

        log_line: list[Any] = [
            timestamp,
            datetime_string,
            state.position.sun_elevation,
            state.aemet_enclosure_state.battery_voltage,
            state.aemet_enclosure_state.logger_panel_temperature,
            state.aemet_enclosure_state.auto_mode,
            state.aemet_enclosure_state.sun_evaluation_by_pyra,
            state.aemet_enclosure_state.sun_evaluation_result,
            state.aemet_enclosure_state.datalogger_software_version,
            state.aemet_enclosure_state.air_pressure_internal,
            state.aemet_enclosure_state.air_pressure_external,
            state.aemet_enclosure_state.relative_humidity_internal,
            state.aemet_enclosure_state.relative_humidity_external,
            state.aemet_enclosure_state.air_temperature_internal,
            state.aemet_enclosure_state.air_temperature_external,
            state.aemet_enclosure_state.dew_point_temperature_internal,
            state.aemet_enclosure_state.dew_point_temperature_external,
            state.aemet_enclosure_state.wind_direction,
            state.aemet_enclosure_state.wind_velocity,
            state.aemet_enclosure_state.rain_sensor_counter_1,
            state.aemet_enclosure_state.rain_sensor_counter_2,
            state.aemet_enclosure_state.closed_due_to_rain,
            state.aemet_enclosure_state.closed_due_to_external_relative_humidity,
            state.aemet_enclosure_state.closed_due_to_external_air_temperature,
            state.aemet_enclosure_state.closed_due_to_internal_relative_humidity,
            state.aemet_enclosure_state.closed_due_to_internal_air_temperature,
            state.aemet_enclosure_state.closed_due_to_wind_velocity,
            state.aemet_enclosure_state.alert_level,
            state.aemet_enclosure_state.averia_fault_code,
            state.aemet_enclosure_state.cover_status,
            state.aemet_enclosure_state.motor_position,
            state.aemet_enclosure_state.em27_has_power,
            state.aemet_enclosure_state.em27_voltage,
            state.aemet_enclosure_state.em27_current,
            state.aemet_enclosure_state.em27_power,
        ]
        stringed_log_line = [str(item).lower() if item is not None else "null" for item in log_line]
        current_log_file = os.path.join(
            _PROJECT_DIR,
            "logs",
            "aemet-enclosure",
            f"{config.general.station_id}-aemet-enclosure-logs-{now.strftime('%Y-%m-%d')}.csv",
        )
        if not os.path.isfile(current_log_file):
            with open(current_log_file, "w") as f:
                f.write(
                    ",".join(
                        [
                            "timestamp",
                            "datetime",
                            "sun_elevation",
                            "battery_voltage",
                            "logger_panel_temperature",
                            "auto_mode",
                            "sun_evaluation_by_pyra",
                            "sun_evaluation_result",
                            "datalogger_software_version",
                            "air_pressure_internal",
                            "air_pressure_external",
                            "relative_humidity_internal",
                            "relative_humidity_external",
                            "air_temperature_internal",
                            "air_temperature_external",
                            "dew_point_temperature_internal",
                            "dew_point_temperature_external",
                            "wind_direction",
                            "wind_velocity",
                            "rain_sensor_counter_1",
                            "rain_sensor_counter_2",
                            "closed_due_to_rain",
                            "closed_due_to_external_relative_humidity",
                            "closed_due_to_external_air_temperature",
                            "closed_due_to_internal_relative_humidity",
                            "closed_due_to_internal_air_temperature",
                            "closed_due_to_wind_velocity",
                            "alert_level",
                            "averia_fault_code",
                            "cover_status",
                            "motor_position",
                            "em27_has_power",
                            "em27_voltage",
                            "em27_current",
                            "em27_power",
                        ]
                    )
                    + "\n"
                )
        with open(current_log_file, "a") as f:
            f.write(",".join(stringed_log_line) + "\n")
