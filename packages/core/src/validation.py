import logging
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"


class Validation:
    @staticmethod
    def check_setup_config():
        try:
            assert os.path.isfile(SETUP_FILE_PATH), "file does not exist"
        except AssertionError as a:
            logging.error(f"Error in setup file: {a}")

    @staticmethod
    def check_parameters_config():
        try:
            assert os.path.isfile(PARAMS_FILE_PATH), "file does not exist"
        except AssertionError as a:
            logging.error(f"Error in parameters file: {a}")
