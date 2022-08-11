import json
import subprocess
import os
from deepdiff import DeepDiff
from ..fixtures import original_config

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


def assert_config_file_content(expected_content: dict, message: str):
    with open(CONFIG_FILE_PATH, "r") as f:
        actual_content = json.load(f)

    print(f"actual_content: {json.dumps(actual_content, indent=4)}")
    print(f"expected_content: {json.dumps(expected_content, indent=4)}")

    difference = DeepDiff(expected_content, actual_content)
    assert difference == {}, f"{message}: {difference}"


def run_cli_command(command: list[str]):
    process = subprocess.run(
        [INTERPRETER_PATH, PYRA_CLI_PATH, *command],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout = process.stdout.decode()
    stderr = process.stderr.decode()
    print(f"stdout: {stdout}", end="")
    print(f"stderr: {stderr}", end="\n\n")
    assert process.returncode == 0
    return stdout


def test_get_config(original_config):
    # get config from cli
    stdout = run_cli_command(["config", "get"])
    config_object_1 = json.loads(stdout)

    # get config from file
    assert_config_file_content(config_object_1, "output from cli does not match file content")


def test_validate_current_config(original_config):
    stdout = run_cli_command(["config", "validate"])
    assert stdout.startswith("Current config file is valid")


def test_update_config(original_config):

    updates = [
        {"general": {"seconds_per_core_interval": False}},
        {"opus": {"experiment_path": "definitely-not-a-path"}},
        {"camtracker": {"sun_intensity_path": 10}},
        {"error_email": {"unknown-key": 10}},
        {"measurement_decision": {"mode": "valid-type-but-invalid-value"}},
        {"measurement_triggers": {"start_time": {"hour": "10", "invalid-key": 0}}},
        {"measurement_triggers": {"max_sun_elevation": 100}},
    ]

    # run "pyra-cli config update" for some invalid variables
    for update in updates:
        stdout = run_cli_command(["config", "update", json.dumps(update)])
        assert "Error in new config string" in stdout

    assert_config_file_content(original_config, "config.json should not have changed")

    updates = [
        {"general": {"seconds_per_core_interval": 400}},
        {"opus": {"em27_ip": "17.17.17.17"}},
        {"camtracker": {"motor_offset_threshold": 40.7}},
        {"error_email": {"sender_password": "very very very secure password"}},
        {"measurement_triggers": {"stop_time": {"hour": 7, "minute": 0}}},
    ]

    def transform(o: dict, i: int):
        if i == 0:
            o["general"]["seconds_per_core_interval"] = 400
        if i == 1:
            o["opus"]["em27_ip"] = "17.17.17.17"
        if i == 2:
            o["camtracker"]["motor_offset_threshold"] = 40.7
        if i == 3:
            o["error_email"]["sender_password"] = "very very very secure password"
        if i == 4:
            o["measurement_triggers"]["stop_time"]["hour"] = 7
            o["measurement_triggers"]["stop_time"]["minute"] = 0
        return o

    # run "pyra-cli config update" for some valid variables
    for index, update in enumerate(updates):
        stdout = run_cli_command(["config", "update", json.dumps(update)])
        assert "Updated config file" in stdout
        original_config = transform(original_config, index)

        assert_config_file_content(original_config, "config.json did not update as expected")


def test_add_default_config(original_config):

    cases = {"helios": None, "tum_plc": None}

    for c in cases:
        with open(os.path.join(PROJECT_DIR, "config", f"{c}.config.default.json"), "r") as f:
            cases[c] = json.load(f)

    for c in cases:
        stdout = run_cli_command(["config", "update", json.dumps({c: None})])
        assert "Updated config file" in stdout
        original_config[c] = None

    assert_config_file_content(original_config, "config.json is in an unexpected state")

    for c in cases:
        stdout = run_cli_command(["config", "update", json.dumps({c: cases[c]})])
        assert "Updated config file" in stdout
        original_config[c] = cases[c]
        assert_config_file_content(
            original_config, f'config.json does not include the "{c}" config'
        )
