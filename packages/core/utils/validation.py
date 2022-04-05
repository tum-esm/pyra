import json
import os
import cerberus
from packages.core.utils.logger import Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"


def file_path_exists(field, value, error):
    if not os.path.isfile(value):
        error(field, "Path has to be an existing file")


def directory_path_exists(field, value, error):
    if not os.path.isdir(value):
        error(field, "Path has to be an existing directory")


def is_valid_ip_adress(field, value, error):
    try:
        assert len(value.split(".")) == 4
        assert all([n.isnumeric() for n in value.split(".")])
        assert all([(int(n) >= 0) and (int(n) <= 255) for n in value.split(".")])
    except AssertionError:
        error(field, "String has to be a valid IPv4 address")


# TODO: Add required JSON schema here (https://docs.python-cerberus.org/en/stable/)
SETUP_FILE_SCHEMA = {
    "enclosure": {
        "type": "dict",
        "schema": {"tum_enclosure_is_present": {"type": "boolean"}},
    },
    "em27": {
        "type": "dict",
        "schema": {"ip": {"type": "string", "check_with": is_valid_ip_adress}},
    },
    "plc": {
        "type": "dict",
        "schema": {
            "is_present": {"type": "boolean"},
            "ip": {"type": "string", "check_with": is_valid_ip_adress},
        },
    },
    "camtracker": {
        "type": "dict",
        "schema": {
            "executable_path": {"type": "string", "check_with": file_path_exists},
            "learn_az_elev_path": {"type": "string", "check_with": file_path_exists},
            "sun_intensity_path": {"type": "string", "check_with": file_path_exists},
            "config_path": {"type": "string", "check_with": file_path_exists},
        },
    },
    "opus": {
        "type": "dict",
        "schema": {
            "executable_path": {"type": "string", "check_with": file_path_exists}
        },
    },
    "vbdsd": {
        "type": "dict",
        "schema": {
            "sensor_is_present": {"type": "boolean"},
            "cam_id": {"type": "number"},
            "image_storage_path": {
                "type": "string",
                "check_with": directory_path_exists,
            },
        },
    },
}

PARAMS_FILE_SCHEMA = {
    "opus": {
        "type": "dict",
        "schema": {
            "executable_parameter": {"type": "string"},
            "macro_path": {"type": "string", "check_with": file_path_exists},
            "experiment_path": {"type": "string", "check_with": file_path_exists},
        },
    },
    "pyra": {
        "type": "dict",
        "schema": {
            "seconds_per_iteration": {"type": "number", "min": 1},
            "test_mode": {"type": "boolean"},
            "automation_is_running": {"type": "boolean"},
        },
    },
    "camtracker": {
        "type": "dict",
        "schema": {"motor_offset_treshold": {"type": "number", "min": 0}},
    },
    "vbdsd": {
        "type": "dict",
        "schema": {
            "interval_time": {"type": "number", "min": 0},
            "evaluation_size": {"type": "number", "min": 0},
            "measurement_threshold": {"type": "number", "min": 0},
            "min_angle": {"type": "number", "min": 0},
        },
    },
    "em27": {
        "type": "dict",
        "schema": {"power_min_angle": {"type": "number", "min": 0}},
    },
}


class CerberusException(Exception):
    pass


class Validation:
    logging_handler = Logger.error

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
            # TODO: Add checks that cannot be done with cerberus here
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
            # TODO: Add checks that cannot be done with cerberus here
            return True
        except (AssertionError, CerberusException) as e:
            Validation.logging_handler(f"{logging_message}{e}")
            return False
