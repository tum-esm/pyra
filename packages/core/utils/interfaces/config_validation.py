import json
import os
from typing import Tuple
from xmlrpc.client import boolean
import cerberus  # type: ignore
from packages.core.utils import Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


def _directory_path_exists(field, value, error):  # type: ignore
    if not os.path.isfile(value):
        error(field, "Path has to be an existing file")


def _file_path_exists(field, value, error):  # type: ignore
    if not os.path.isfile(value):
        error(field, "Path has to be an existing file")


def _is_valid_ip_adress(field, value, error):
    try:
        assert len(value.split(".")) == 4
        assert all([n.isnumeric() for n in value.split(".")])
        assert all([(int(n) >= 0) and (int(n) <= 255) for n in value.split(".")])
    except AssertionError:
        error(field, "String has to be a valid IPv4 address")


def get_dict_schema(s: dict) -> dict:
    return {"type": "dict", "schema": s}


def get_nullable_dict_schema(s: dict) -> dict:
    return {"type": "dict", "schema": s, "nullable": True}


def get_config_file_schema(strict: boolean):
    """
    Returns a cerberus schema for the config. With strict=false,
    the checks whether file paths or directories exist will be
    skipped. Strict-mode is used by the core, Loose-mode is used
    by the CLI (which has to work even with invalid paths).
    """

    specs = {
        "ip": {"type": "string", "check_with": _is_valid_ip_adress},
        "file": {"type": "string"},
        "directory": {"type": "string"},
        "time": {
            "type": "dict",
            "schema": {
                "hour": {"type": "integer", "min": 0, "max": 23},
                "minute": {"type": "integer", "min": 0, "max": 59},
                "second": {"type": "integer", "min": 0, "max": 59},
            },
        },
    }

    if strict:
        specs["file"]["check_with"] = _file_path_exists
        specs["directory"]["check_with"] = _directory_path_exists

    return {
        "general": get_dict_schema(
            {
                "seconds_per_core_interval": {
                    "type": "number",
                    "min": 5,
                    "max": 600,
                },
                "test_mode": {"type": "boolean"},
                "station_id": {"type": "string"},
                "min_sun_elevation": {"type": "number", "min": 0, "max": 90},
            }
        ),
        "opus": get_dict_schema(
            {
                "em27_ip": specs["ip"],
                "executable_path": specs["file"],
                "experiment_path": specs["file"],
                "macro_path": specs["file"],
                "username": {"type": "string"},
                "password": {"type": "string"},
            }
        ),
        "camtracker": get_dict_schema(
            {
                "config_path": specs["file"],
                "executable_path": specs["file"],
                "learn_az_elev_path": specs["file"],
                "sun_intensity_path": specs["file"],
                "motor_offset_threshold": {
                    "type": "number",
                    "min": -360,
                    "max": 360,
                },
            }
        ),
        "error_email": get_dict_schema(
            {
                "sender_address": {"type": "string"},
                "sender_password": {"type": "string"},
                "notify_recipients": {"type": "boolean"},
                "recipients": {"type": "string"},
            }
        ),
        "measurement_decision": get_dict_schema(
            {
                "mode": {
                    "type": "string",
                    "allowed": ["automatic", "manual", "cli"],
                },
                "manual_decision_result": {"type": "boolean"},
                "cli_decision_result": {"type": "boolean"},
            }
        ),
        "measurement_triggers": get_dict_schema(
            {
                "consider_time": {"type": "boolean"},
                "consider_sun_elevation": {"type": "boolean"},
                "consider_helios": {"type": "boolean"},
                "start_time": specs["time"],
                "stop_time": specs["time"],
                "min_sun_elevation": {"type": "number", "min": 0, "max": 90},
            }
        ),
        "tum_plc": get_nullable_dict_schema(
            {
                "ip": specs["ip"],
                "version": {"type": "integer", "allowed": [1, 2]},
                "controlled_by_user": {"type": "boolean"},
            }
        ),
        "helios": get_nullable_dict_schema(
            {
                "camera_id": {"type": "integer", "min": 0, "max": 999999},
                "evaluation_size": {"type": "integer", "min": 1, "max": 100},
                "seconds_per_interval": {
                    "type": "number",
                    "min": 5,
                    "max": 600,
                },
                "measurement_threshold": {
                    "type": "number",
                    "min": 0.1,
                    "max": 1,
                },
                "save_images": {"type": "boolean"},
            }
        ),
        "upload": get_nullable_dict_schema(
            {
                "is_active": {"type": "boolean"},
                "host": specs["ip"],
                "user": {"type": "string"},
                "password": {"type": "string"},
                "src_directory": specs["file"],
                "dst_directory": {"type": "string"},
                "remove_src_after_upload": {"type": "boolean"},
            }
        ),
    }


class CerberusException(Exception):
    pass


logger = Logger(origin="config-validation")


class ConfigValidation:
    """
    Functions used to validate config objects/files.

    All functions in here do not used filelocks because
    higher level functions should do that.
    """

    logging_handler = logger.error

    @staticmethod
    def check_dict(
        content_object: dict, partial_validation: bool = False, validate_paths: bool = True
    ) -> None:
        """
        For a given config object, check its integrity.

        "partial_validation" means that keys can be missing.
        This is used when updating the config via CLI, since
        the errors given when updating should only concern
        the passed properties).

        "validate_paths" means that paths (files and directories)
        contained in the config object should be checked too -
        whether they exist. This path-validation is skipped when
        reading the config via CLI because the UI can and should
        deal with invalid paths but not with an invalid structure.

        Does not return anything, only raises AssertionErrors.
        """
        validator = cerberus.Validator(
            get_config_file_schema(strict=validate_paths),
            require_all=(not partial_validation),
        )
        assert validator.validate(content_object), validator.errors
        # Add assertions that cannot be done with cerberus here

    @staticmethod
    def check_current_config_file() -> Tuple[bool, Exception]:
        """
        Load the contents of the current config file and
        validate its full integrity (with filepaths).
        """
        try:
            assert os.path.isfile(CONFIG_FILE_PATH), "file does not exist"
            with open(CONFIG_FILE_PATH, "r") as f:
                try:
                    content_object = json.load(f)
                except:
                    raise AssertionError("file not in a valid json format")

            ConfigValidation.check_dict(content_object, partial_validation=False)
            return True, Exception("")
        except Exception as e:
            ConfigValidation.logging_handler(f"Error in current config file: {e}")
            return False, e

    @staticmethod
    def check_partial_config_string(content: str) -> bool:
        """
        For a given string, check whether its is a valid
        partial config object. Used in CLI.
        """
        try:
            try:
                content_dict = json.loads(content)
            except:
                raise AssertionError("content not in a valid json format")

            ConfigValidation.check_dict(content_dict, partial_validation=True)
            return True
        except Exception as e:
            ConfigValidation.logging_handler(f"Error in new config string: {e}")
            return False
