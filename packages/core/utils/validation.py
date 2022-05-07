import json
import os
import cerberus
from packages.core.utils.logger import Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"


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


# TODO: Add config json schemas to documentation

FILE_SCHEMA = {"type": "string", "check_with": _file_path_exists}
DIR_SCHEMA = {"type": "string", "check_with": _directory_path_exists}
IP_SCHEMA = {"type": "string", "check_with": _is_valid_ip_adress}
DICT_SCHEMA = lambda schema: {"type": "dict", "schema": schema}
INT_LIST_SCHEMA = lambda length: {
    "type": "list",
    "schema": {"type": "integer"},
    "minlength": length,
    "maxlength": length,
}
INT_SCHEMA = {"type": "integer"}
BOOL_SCHEMA = {"type": "boolean"}

SETUP_FILE_SCHEMA = {
    "camtracker": DICT_SCHEMA(
        {
            "config_path": FILE_SCHEMA,
            "executable_path": FILE_SCHEMA,
            "learn_az_elev_path": FILE_SCHEMA,
            "sun_intensity_path": FILE_SCHEMA,
        }
    ),
    "em27": DICT_SCHEMA({"ip": IP_SCHEMA}),
    "enclosure": DICT_SCHEMA({"tum_enclosure_is_present": {"type": "boolean"}}),
    "opus": DICT_SCHEMA({"executable_path": FILE_SCHEMA}),
    "plc": DICT_SCHEMA(
        {
            "actors": DICT_SCHEMA(
                {
                    "current_angle": INT_LIST_SCHEMA(3),
                    "fan_speed": INT_LIST_SCHEMA(3),
                    "move_cover": INT_LIST_SCHEMA(3),
                    "nominal_angle": INT_LIST_SCHEMA(3),
                }
            ),
            "control": DICT_SCHEMA(
                {
                    "auto_temp_mode": INT_LIST_SCHEMA(4),
                    "manual_control": INT_LIST_SCHEMA(4),
                    "manual_temp_mode": INT_LIST_SCHEMA(4),
                    "reset": INT_LIST_SCHEMA(4),
                    "sync_to_tracker": INT_LIST_SCHEMA(4),
                }
            ),
            "is_present": {"type": "boolean"},
            "ip": IP_SCHEMA,
            "power": DICT_SCHEMA(
                {
                    "camera": INT_LIST_SCHEMA(4),
                    "computer": INT_LIST_SCHEMA(4),
                    "heater": INT_LIST_SCHEMA(4),
                    "router": INT_LIST_SCHEMA(4),
                    "spectrometer": INT_LIST_SCHEMA(4),
                }
            ),
            "sensors": DICT_SCHEMA(
                {
                    "humidity": INT_LIST_SCHEMA(3),
                    "temperature": INT_LIST_SCHEMA(3),
                }
            ),
            "state": DICT_SCHEMA(
                {
                    "camera": INT_LIST_SCHEMA(4),
                    "computer": INT_LIST_SCHEMA(4),
                    "cover": INT_LIST_SCHEMA(4),
                    "heater": INT_LIST_SCHEMA(4),
                    "motor_failed": INT_LIST_SCHEMA(4),
                    "rain": INT_LIST_SCHEMA(4),
                    "reset_needed": INT_LIST_SCHEMA(4),
                    "router": INT_LIST_SCHEMA(4),
                    "spectrometer": INT_LIST_SCHEMA(4),
                    "ups_alert": INT_LIST_SCHEMA(4),
                }
            ),
        }
    ),
    "vbdsd": DICT_SCHEMA(
        {
            "is_present": {"type": "boolean"},
            "cam_id": {"type": "integer"},
            "image_storage_path": DIR_SCHEMA,
        }
    ),
}

PARAMS_FILE_SCHEMA = {
    "camtracker": DICT_SCHEMA({"motor_offset_threshold": {"type": "number"}}),
    "em27": DICT_SCHEMA({"power_min_angle": {"type": "number"}}),
    "opus": DICT_SCHEMA(
        {
            "executable_parameter": {"type": "string"},
            "experiment_path": FILE_SCHEMA,
            "macro_path": FILE_SCHEMA,
        }
    ),
    "pyra": DICT_SCHEMA(
        {
            "seconds_per_iteration": {"type": "number"},
            "test_mode": {"type": "boolean"},
        }
    ),
    "vbdsd": DICT_SCHEMA(
        {
            "evaluation_size": {"type": "integer"},
            "interval_time": {"type": "number"},
            "measurement_threshold": {"type": "number"},
            "min_sun_angle": {"type": "number"},
        }
    ),
    "enclosure": DICT_SCHEMA(
        {
            "min_sun_angle": {"type": "number"},
        }
    ),
    "measurement_triggers": DICT_SCHEMA(
        {
            "type": DICT_SCHEMA(
                {
                    "time": {"type": "boolean"},
                    "sun_angle": {"type": "boolean"},
                    "vbdsd": {"type": "boolean"},
                    "user_control": {"type": "boolean"},
                }
            ),
            "start_time": INT_LIST_SCHEMA(3),
            "stop_time": INT_LIST_SCHEMA(3),
            "user_trigger_present": {"type": "boolean"},
            "sun_angle_start": {"type": "number"},
            "sun_angle_stop": {"type": "number"},
        }
    ),
    "measurement_conditions": DICT_SCHEMA({"current_sun_angle": {"type": "number"}}),
}


class CerberusException(Exception):
    pass


class Validation:
    logging_handler = Logger().error

    @staticmethod
    def __load_json(file_path, content_string, validator):
        if content_string is None:
            assert os.path.isfile(file_path), "file does not exist"
            with open(file_path, "r") as f:
                try:
                    content = json.load(f)
                except:
                    raise AssertionError("file not in a valid json format")
        else:
            try:
                content = json.loads(content_string)
            except:
                raise AssertionError("content not in a valid json format")

        if not validator.validate(content):
            raise CerberusException(validator.errors)

        return content

    @staticmethod
    def check_setup_file(
        file_path=SETUP_FILE_PATH,
        content_string=None,
        logging_message="Error in current setup file: ",
        partial_validation=False,
    ):
        try:
            validator = cerberus.Validator(
                SETUP_FILE_SCHEMA, require_all=(not partial_validation)
            )
            content = Validation.__load_json(file_path, content_string, validator)
            # Add checks that cannot be done with cerberus here
            return True
        except (AssertionError, CerberusException) as e:
            Validation.logging_handler(f"{logging_message}{e}")
            return False

    @staticmethod
    def check_parameters_file(
        file_path=PARAMS_FILE_PATH,
        content_string=None,
        logging_message="Error in current parameters file: ",
        partial_validation=False,
    ):
        try:
            validator = cerberus.Validator(
                PARAMS_FILE_SCHEMA, require_all=(not partial_validation)
            )
            content = Validation.__load_json(file_path, content_string, validator)
            # Add checks that cannot be done with cerberus here
            return True
        except (AssertionError, CerberusException) as e:
            Validation.logging_handler(f"{logging_message}{e}")
            return False
