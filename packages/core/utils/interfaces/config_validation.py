import json
import os
import cerberus
from packages.core.utils import Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


def _file_path_exists(field, value, error):
    if not os.path.isfile(value):
        error(field, "Path has to be an existing file")


def _is_valid_ip_adress(field, value, error):
    try:
        assert len(value.split(".")) == 4
        assert all([n.isnumeric() for n in value.split(".")])
        assert all([(int(n) >= 0) and (int(n) <= 255) for n in value.split(".")])
    except AssertionError:
        error(field, "String has to be a valid IPv4 address")


DICT_SCHEMA = lambda s: {"type": "dict", "schema": s}
NULLABLE_DICT_SCHEMA = lambda s: {"type": "dict", "schema": s, "nullable": True}


class _Schemas:
    time_dict = {
        "type": "dict",
        "schema": {
            "hour": {"type": "integer", "min": 0, "max": 23},
            "minute": {"type": "integer", "min": 0, "max": 59},
            "second": {"type": "integer", "min": 0, "max": 59},
        },
    }
    string = {"type": "string"}
    boolean = {"type": "boolean"}
    ip = {"type": "string", "check_with": _is_valid_ip_adress}
    file = {"type": "string", "check_with": _file_path_exists}


CONFIG_FILE_SCHEMA = {
    "general": DICT_SCHEMA(
        {
            "seconds_per_core_interval": {"type": "number", "min": 5, "max": 600},
            "test_mode": _Schemas.boolean,
            "station_id": {"type": "string"},
        }
    ),
    "opus": DICT_SCHEMA(
        {
            "em27_ip": _Schemas.ip,
            "executable_path": _Schemas.file,
            "executable_parameter": _Schemas.string,
            "experiment_path": _Schemas.file,
            "macro_path": _Schemas.file,
        }
    ),
    "camtracker": DICT_SCHEMA(
        {
            "config_path": _Schemas.file,
            "executable_path": _Schemas.file,
            "learn_az_elev_path": _Schemas.file,
            "sun_intensity_path": _Schemas.file,
            "motor_offset_threshold": {"type": "number", "min": -360, "max": 360},
        }
    ),
    "error_email": DICT_SCHEMA(
        {
            "sender_address": _Schemas.string,
            "sender_password": _Schemas.string,
            "notify_recipients": _Schemas.boolean,
            "recipients": _Schemas.string,
        }
    ),
    "measurement_decision": DICT_SCHEMA(
        {
            "mode": {"type": "string", "allowed": ["automatic", "manual", "cli"]},
            "manual_decision_result": _Schemas.boolean,
            "cli_decision_result": _Schemas.boolean,
        }
    ),
    "measurement_triggers": DICT_SCHEMA(
        {
            "consider_time": _Schemas.boolean,
            "consider_sun_elevation": _Schemas.boolean,
            "consider_vbdsd": _Schemas.boolean,
            "start_time": _Schemas.time_dict,
            "stop_time": _Schemas.time_dict,
            "min_sun_elevation": {"type": "number", "min": 0, "max": 90},
            "max_sun_elevation": {"type": "number", "min": 0, "max": 90},
        }
    ),
    "tum_plc": NULLABLE_DICT_SCHEMA(
        {
            "min_power_elevation": {"type": "number", "min": 0, "max": 90},
            "ip": _Schemas.ip,
            "version": {"type": "integer", "allowed": [1, 2]},
            "controlled_by_user": {"type": "boolean"},
        }
    ),
    "vbdsd": NULLABLE_DICT_SCHEMA(
        {
            "camera_id": {"type": "integer", "min": 0, "max": 999999},
            "evaluation_size": {"type": "integer", "min": 1, "max": 100},
            "seconds_per_interval": {"type": "number", "min": 5, "max": 600},
            "measurement_threshold": {"type": "number", "min": 0.1, "max": 1},
            "min_sun_elevation": {"type": "number", "min": 0, "max": 90},
        }
    ),
}


class CerberusException(Exception):
    pass


class ConfigValidation:
    logging_handler = Logger().error

    @staticmethod
    def check(
        content_object: dict,
        partial_validation: bool = False,
    ):
        validator = cerberus.Validator(
            CONFIG_FILE_SCHEMA, require_all=(not partial_validation)
        )
        assert validator.validate(content_object), validator.errors
        # Add assertions that cannot be done with cerberus here

    @staticmethod
    def check_current_config_file():
        try:
            assert os.path.isfile(CONFIG_FILE_PATH), "file does not exist"
            with open(CONFIG_FILE_PATH, "r") as f:
                try:
                    content_object = json.load(f)
                except:
                    raise AssertionError("file not in a valid json format")

            ConfigValidation.check(content_object, partial_validation=False)
            return True
        except Exception as e:
            ConfigValidation.logging_handler(f"Error in current config file: {e}")
            return False

    @staticmethod
    def check_partial_config_string(content: str):
        try:
            try:
                content_object = json.loads(content)
            except:
                raise AssertionError("content not in a valid json format")

            ConfigValidation.check(content_object, partial_validation=True)
            return True
        except Exception as e:
            ConfigValidation.logging_handler(f"Error in new config string: {e}")
            return False
