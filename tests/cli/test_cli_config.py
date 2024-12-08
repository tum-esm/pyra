import json
import subprocess
import sys
from packages.core import types
import pytest
import os
from tum_esm_utils.validators import StrictIPv4Adress
from ..fixtures import sample_config

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
INTERPRETER_PATH = sys.executable
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


def assert_config_file_content(expected_content: types.Config, message: str) -> None:
    actual_content = types.Config.load(ignore_path_existence=True)
    print(f"actual_content: {actual_content.model_dump_json(indent=4)}")
    print(f"expected_content: {expected_content.model_dump_json(indent=4)}")
    assert expected_content == actual_content, message


def run_cli_command(
    command: list[str], should_succeed: bool = False, should_fail: bool = False
) -> str:
    process = subprocess.run(
        [INTERPRETER_PATH, PYRA_CLI_PATH, *command],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout = process.stdout.decode()
    stderr = process.stderr.decode()
    print(f"command: {command}")
    print("stdout: " + stdout.strip(' \n'))
    print("stderr: " + stderr.strip(' \n'), end="\n\n")
    if should_succeed:
        assert process.returncode == 0
    if should_fail:
        assert process.returncode != 0
    return stdout


@pytest.mark.order(3)
@pytest.mark.ci
def test_get_config(sample_config: types.Config) -> None:
    # get config from cli
    stdout = run_cli_command(["config", "get"], should_succeed=True)
    config_object_1 = types.Config.model_validate_json(
        stdout, context={"ignore_path_existence": True}
    )

    # get config from file
    assert_config_file_content(config_object_1, "output from cli does not match file content")


@pytest.mark.order(3)
@pytest.mark.ci
def test_validate_current_config(sample_config: types.Config) -> None:
    stdout = run_cli_command(["config", "validate"], should_succeed=True)
    assert stdout.startswith("Current config file is valid")


@pytest.mark.order(3)
@pytest.mark.ci
def test_update_config(sample_config: types.Config) -> None:

    updates = [
        {"general": {"seconds_per_core_interval": False}},
        {"opus": {"experiment_path": ["should not be an array"]}},
        {"camtracker": {"sun_intensity_path": 10}},
        {"error_email": {"unknown-key": 10}},
        {"measurement_decision": {"mode": "valid-type-but-invalid-value"}},
        {"measurement_triggers": {"start_time": {"hour": "10", "invalid-key": 0}}},
        {"measurement_triggers": {"max_sun_elevation": 100}},
    ]

    # run "pyra-cli config update" for some invalid variables
    for update in updates:
        stdout = run_cli_command(["config", "update", json.dumps(update)], should_fail=True)
        assert "Config update is invalid" in stdout

    assert_config_file_content(sample_config, "config.json should not have changed")

    updates = [
        {"general": {"seconds_per_core_interval": 400}},
        {"opus": {"em27_ip": "17.17.17.17"}},
        {"camtracker": {"motor_offset_threshold": 40.7}},
        {"error_email": {"smtp_password": "very very very secure password"}},
        {"measurement_triggers": {"stop_time": {"hour": 7, "minute": 0}}},
    ]

    def transform(config: types.Config, i: int) -> types.Config:
        if i == 0:
            config.general.seconds_per_core_interval = 400
        if i == 1:
            config.opus.em27_ip = StrictIPv4Adress(root="17.17.17.17")
        if i == 2:
            config.camtracker.motor_offset_threshold = 40.7
        if i == 3:
            config.error_email.smtp_password = "very very very secure password"
        if i == 4:
            config.measurement_triggers.stop_time.hour = 7
            config.measurement_triggers.stop_time.minute = 0
        return config

    # run "pyra-cli config update" for some valid variables
    for index, update in enumerate(updates):
        stdout = run_cli_command(["config", "update", json.dumps(update)], should_succeed=True)
        assert "Updated config file" in stdout
        sample_config = transform(sample_config, index)

        assert_config_file_content(sample_config, "config.json did not update as expected")


@pytest.mark.order(3)
@pytest.mark.ci
def test_add_default_config(sample_config: types.Config) -> None:

    cases = ["helios", "tum_enclosure"]

    for c in cases:
        stdout = run_cli_command(["config", "update", json.dumps({c: None})], should_succeed=True)
        assert "Updated config file" in stdout
        if c == "helios":
            sample_config.helios = None
        if c == "tum_enclosure":
            sample_config.tum_enclosure = None

    assert_config_file_content(sample_config, "config.json is in an unexpected state")

    for c in cases:
        with open(os.path.join(PROJECT_DIR, "config", f"{c}.config.default.json"), "r") as f:
            default_subconfig = json.load(f)
        stdout = run_cli_command(["config", "update",
                                  json.dumps({c: default_subconfig})],
                                 should_succeed=True)
        assert "Updated config file" in stdout
        if c == "helios":
            sample_config.helios = types.config.HeliosConfig.model_validate(default_subconfig)
        if c == "tum_enclosure":
            sample_config.tum_enclosure = types.tum_enclosure.TUMEnclosureConfig.model_validate(
                default_subconfig
            )
        assert_config_file_content(sample_config, f'config.json does not include the "{c}" config')
