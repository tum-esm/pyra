import json
import subprocess
import os
from deepdiff import DeepDiff
from . import config_file

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")

CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_FILE_PATH_TMP = os.path.join(PROJECT_DIR, "config", "config.tmp.json")


def test_get_config(config_file):
    # get config from cli
    process = subprocess.run(
        [INTERPRETER_PATH, PYRA_CLI_PATH, "config", "get"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout = process.stdout.decode()
    stderr = process.stderr.decode()
    print(f"stdout: {stdout}")
    print(f"stderr: {stderr}")

    assert process.returncode == 0
    config_object_1 = json.loads(stdout)

    # get config from file
    with open(CONFIG_FILE_PATH, "r") as f:
        config_object_2 = json.load(f)

    # assert equality
    difference = DeepDiff(config_object_1, config_object_2)
    assert difference == {}, difference


"""
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
"""
