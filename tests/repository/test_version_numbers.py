import json
import os
import sys
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)


@pytest.mark.ci
def test_default_config() -> None:

    with open(os.path.join(PROJECT_DIR, "pyproject.toml"), "r") as f:
        third_line = f.read().split("\n")[2]
        assert third_line.startswith("version = ")
        pyproject_version = third_line.split(" = ")[1].strip('"')

    cli_info_stdout = tum_esm_utils.shell.run_shell_command(
        f"{sys.executable} ./packages/cli/main.py info",
        working_directory=PROJECT_DIR
    ).strip(" \n")
    assert cli_info_stdout == f'This CLI is running Pyra version {pyproject_version} in directory "{PROJECT_DIR}"'

    with open(
        os.path.join(PROJECT_DIR, "config", "config.default.json"), "r"
    ) as f:
        default_config_version = json.load(f)["general"]["version"]
    assert default_config_version == pyproject_version

    with open(
        os.path.join(PROJECT_DIR, "packages", "ui", "package.json"), "r"
    ) as f:
        ui_package_version = json.load(f)["version"]
    assert ui_package_version == pyproject_version

    with open(
        os.path.join(PROJECT_DIR, "packages", "ui", "src-tauri", "Cargo.toml"),
        "r"
    ) as f:
        third_line = f.read().split("\n")[2]
        assert third_line.startswith("version = ")
        cargo_version = third_line.split(" = ")[1].strip('"')
    assert cargo_version == pyproject_version

    with open(
        os.path.join(
            PROJECT_DIR, "packages", "ui", "src-tauri", "tauri.conf.json"
        ), "r"
    ) as f:
        tauri_conf_version = json.load(f)["package"]["version"]
    assert tauri_conf_version == pyproject_version
