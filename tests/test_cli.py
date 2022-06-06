import json
import subprocess
import os
from deepdiff import DeepDiff
from . import original_config

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


def assert_config_file_content(expected_content: dict, message: str):
    with open(CONFIG_FILE_PATH, "r") as f:
        actual_content = json.load(f)

    difference = DeepDiff(expected_content, actual_content)
    assert difference == {}, f"{message}: {difference}"


def assert_current_config_validity(verbose: bool = False):
    process = subprocess.run(
        [INTERPRETER_PATH, PYRA_CLI_PATH, "config", "validate"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout = process.stdout.decode()
    stderr = process.stderr.decode()
    if verbose:
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")

    assert process.returncode == 0
    assert stdout.startswith("Current config file is valid")


def test_get_config(original_config):
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
    assert_config_file_content(
        config_object_1, "output from cli does not match file content"
    )


def test_validate_current_config(original_config):
    assert_current_config_validity(verbose=True)


def test_set_config(original_config):
    # TODO: run "pyra-cli config set" for some invalid variables
    # TODO: Assert failure and unchanged JSON file inbetween

    # TODO: run "pyra-cli config set" for some valid variables
    # TODO: Assert success and changed JSON file inbetween
    pass
