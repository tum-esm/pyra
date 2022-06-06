import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")

# TODO: Buildup = copy config.json to config.tmp.json file
# TODO: Teardown = remove config.json, rename config.tmp.json to config.json


def test_get_config():
    # TODO: run "pyra-cli config get"
    # TODO: load JSON from path
    # TODO: Assert equality
    pass


def test_validate_current_config():
    # TODO: run "pyra-cli config validate"
    # TODO: Assert success
    pass


def test_set_config():
    # TODO: run "pyra-cli config set" for some invalid variables
    # TODO: Assert failure and unchanged JSON file inbetween
    # TODO: run "pyra-cli config set" for some valid variables
    # TODO: Assert success and changed JSON file inbetween
    pass
