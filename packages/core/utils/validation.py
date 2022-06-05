import json
import os
import cerberus
from packages.core.utils.logger import Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


def _file_path_exists(field, value, error):
    if not os.path.isfile(value):
        error(field, "Path has to be an existing file")


def _directory_path_exists(field, value, error):
    if not os.path.isdir(value):
        error(field, "Path has to be an existing directory")


def _is_valid_ip_adress(field, value, error):
    try:
        assert len(value.split(".")) == 4
        assert all([n.isnumeric() for n in value.split(".")])
        assert all([(int(n) >= 0) and (int(n) <= 255) for n in value.split(".")])
    except AssertionError:
        error(field, "String has to be a valid IPv4 address")


DICT_SCHEMA = lambda s: {"type": "dict", "schema": s}
NULLABLE_DICT_SCHEMA = lambda s: {"type": "dict", "schema": s, "nullable": True}


class Schemas:
    sun_elevation = ({"type": "number", "min": 0, "max": 90},)
    time_list = [
        {"type": "integer", "min": 0, "max": 23},
        {"type": "integer", "min": 0, "max": 59},
        {"type": "integer", "min": 0, "max": 59},
    ]
    time_interval = {"type": "number", "min": 5, "max": 600}
    number = {"type": "number"}
    integer = {"type": "integer"}
    string = {"type": "string"}
    boolean = {"type": "boolean"}
    int_list_3 = (
        {
            "type": "list",
            "schema": {"type": "integer"},
            "minlength": 3,
            "maxlength": 3,
        },
    )
    int_list_4 = (
        {
            "type": "list",
            "schema": {"type": "integer"},
            "minlength": 4,
            "maxlength": 4,
        },
    )
    ip = ({"type": "string", "check_with": _is_valid_ip_adress},)
    directory = ({"type": "string", "check_with": _directory_path_exists},)
    file = {"type": "string", "check_with": _file_path_exists}


CONFIG_FILE_SCHEMA = {
    "general": DICT_SCHEMA(
        {
            "enclosure_min_power_elevation": Schemas.sun_elevation,
            "em27_min_power_elevation": Schemas.sun_elevation,
            "seconds_per_core_interval": Schemas.time_interval,
            "test_mode": Schemas.boolean,
        }
    ),
    "opus": DICT_SCHEMA(
        {
            "em27_ip": Schemas.ip,
            "executable_path": Schemas.file,
            "executable_parameter": Schemas.string,
            "experiment_path": Schemas.file,
            "macro_path": Schemas.file,
        }
    ),
    "camtracker": DICT_SCHEMA(
        {
            "config_path": Schemas.file,
            "executable_path": Schemas.file,
            "learn_az_elev_path": Schemas.file,
            "sun_intensity_path": Schemas.file,
            "motor_offset_threshold": Schemas.number,
        }
    ),
    "error_email": DICT_SCHEMA(
        {
            "sender_address": Schemas.string,
            "sender_password": Schemas.string,
            "notify_recipients": Schemas.boolean,
            "recipients": Schemas.string,
        }
    ),
    "measurement_decision": DICT_SCHEMA(
        {
            "mode": {"type": "string", "allowed": ["automatic", "manual", "cli"]},
            "manual_decision_result": Schemas.boolean,
            "cli_decision_result": Schemas.boolean,
        }
    ),
    "measurement_triggers": DICT_SCHEMA(
        {
            "consider_time": Schemas.boolean,
            "consider_sun_elevation": Schemas.boolean,
            "consider_vbdsd": Schemas.boolean,
            "start_time": Schemas.time_list,
            "stop_time": Schemas.time_list,
            "min_sun_elevation": Schemas.sun_elevation,
            "max_sun_elevation": Schemas.sun_elevation,
        }
    ),
    "tum_plc": NULLABLE_DICT_SCHEMA(
        {
            "ip": Schemas.ip,
            "actors": DICT_SCHEMA(
                {
                    "current_angle": Schemas.int_list_3,
                    "fan_speed": Schemas.int_list_3,
                    "move_cover": Schemas.int_list_3,
                    "nominal_angle": Schemas.int_list_3,
                }
            ),
            "control": DICT_SCHEMA(
                {
                    "auto_temp_mode": Schemas.int_list_4,
                    "manual_control": Schemas.int_list_4,
                    "manual_temp_mode": Schemas.int_list_4,
                    "reset": Schemas.int_list_4,
                    "sync_to_tracker": Schemas.int_list_4,
                }
            ),
            "power": DICT_SCHEMA(
                {
                    "camera": Schemas.int_list_4,
                    "computer": Schemas.int_list_4,
                    "heater": Schemas.int_list_4,
                    "router": Schemas.int_list_4,
                    "spectrometer": Schemas.int_list_4,
                }
            ),
            "sensors": DICT_SCHEMA(
                {"humidity": Schemas.int_list_3, "temperature": Schemas.int_list_3}
            ),
            "state": DICT_SCHEMA(
                {
                    "camera": Schemas.int_list_4,
                    "computer": Schemas.int_list_4,
                    "cover_closed": Schemas.int_list_4,
                    "heater": Schemas.int_list_4,
                    "motor_failed": Schemas.int_list_4,
                    "rain": Schemas.int_list_4,
                    "reset_needed": Schemas.int_list_4,
                    "router": Schemas.int_list_4,
                    "spectrometer": Schemas.int_list_4,
                    "ups_alert": Schemas.int_list_4,
                }
            ),
        }
    ),
    "vbdsd": NULLABLE_DICT_SCHEMA(
        {
            "camera_id": {"type": "integer", "min": 0, "max": 999999},
            "evaluation_size": {"type": "integer", "min": 1, "max": 100},
            "seconds_per_interval": Schemas.time_interval,
            "measurement_threshold": {"type": "number", "min": 0.1, "max": 1},
            "min_sun_elevation": Schemas.sun_elevation,
        }
    ),
}


class CerberusException(Exception):
    pass


class Validation:
    logging_handler = Logger().error

    @staticmethod
    def _check(
        file_content: dict,
        partial_validation: bool = False,
    ):
        validator = cerberus.Validator(
            CONFIG_FILE_SCHEMA, require_all=(not partial_validation)
        )
        assert validator.validate(file_content), validator.errors
        # Add assertions that cannot be done with cerberus here

    @staticmethod
    def check_current_config():
        try:
            assert os.path.isfile(CONFIG_FILE_PATH), "file does not exist"
            with open(CONFIG_FILE_PATH, "r") as f:
                try:
                    file_content = json.load(f)
                except:
                    raise AssertionError("file not in a valid json format")

            Validation._check(file_content, partial_validation=False)
            return True
        except Exception as e:
            Validation.logging_handler(f"Error in current config file: {e}")
            return False

    @staticmethod
    def check_config_string(
        content_string,
        partial_validation=False,
    ):
        try:
            try:
                file_content = json.loads(content_string)
            except:
                raise AssertionError("content not in a valid json format")

            Validation._check(file_content, partial_validation)
            return True
        except Exception as e:
            Validation.logging_handler(f"Error in new config string: {e}")
            return False
