import json
import logging
import os
import cerberus

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"

# TODO: Add required JSON schema here (https://docs.python-cerberus.org/en/stable/)
SETUP_FILE_SCHEMA = {}
PARAMS_FILE_SCHEMA = {
    "secondsPerIteration": {"type": "number", "min": 0},
    "test_environment_mode": {"type": "number", "allowed": [0, 1]},
}


class CerberusException(Exception):
    pass


class Validation:
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
        logging_handler=logging.error,
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
            logging_handler(f"{logging_message}{e}")
            return False

    @staticmethod
    def check_parameters_file(
        file_path=PARAMS_FILE_PATH,
        content_string=None,
        logging_handler=logging.error,
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
            logging_handler(f"{logging_message}{e}")
            return False
