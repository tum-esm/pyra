import json
import logging
import os
import cerberus

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"

# TODO: Add required JSON schema here (https://docs.python-cerberus.org/en/stable/)
SETUP_FILE_VALIDATOR = cerberus.Validator({})
PARAMS_FILE_VALIDATOR = cerberus.Validator(
    {"secondsPerIteration": {"type": "number", "min": 0}}
)


class CerberusException(Exception):
    pass


class Validation:
    @staticmethod
    def check_setup_config():
        try:
            assert os.path.isfile(SETUP_FILE_PATH), "file does not exist"
            with open(SETUP_FILE_PATH, "r") as f:
                try:
                    SETUP_FILE_CONTENT = json.load(f)
                except:
                    raise AssertionError("not in a valid json format")

            if not SETUP_FILE_VALIDATOR.validate(SETUP_FILE_CONTENT):
                raise CerberusException(SETUP_FILE_VALIDATOR.errors)
            # TODO: Add checks that cannot be done with cerberus here

        except AssertionError as a:
            logging.error(f"Error in setup file: {a}")
        except CerberusException as v:
            logging.error(f"Error in parameters file: {v}")

    @staticmethod
    def check_parameters_config():
        try:
            assert os.path.isfile(PARAMS_FILE_PATH), "file does not exist"
            with open(PARAMS_FILE_PATH, "r") as f:
                try:
                    PARAMS_FILE_CONTENT = json.load(f)
                except:
                    raise AssertionError("not in a valid json format")

            if not PARAMS_FILE_VALIDATOR.validate(PARAMS_FILE_CONTENT):
                raise CerberusException(PARAMS_FILE_VALIDATOR.errors)
            # TODO: Add checks that cannot be done with cerberus here

        except AssertionError as a:
            logging.error(f"Error in parameters file: {a}")
        except CerberusException as v:
            logging.error(f"Error in parameters file: {v}")
