import subprocess
import os
import time
from packages.core import types
from typing import Any
import pytest
from ..fixtures import sample_config, empty_logs  # pyright: ignore[reportUnusedImport]

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
DEBUG_LOG_PATH = os.path.join(PROJECT_DIR, "logs", "debug.log")


def run_cli_command(command: list[str]) -> str:
    process = subprocess.run(
        ["python", PYRA_CLI_PATH, *command],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout = process.stdout.decode()
    stderr = process.stderr.decode()
    print(f"stdout: {stdout}", end="")
    print(f"stderr: {stderr}", end="\n\n")
    assert process.returncode == 0
    return stdout


@pytest.fixture()
def _stop_pyra_core() -> Any:  # pyright: ignore[reportUnusedFunction]
    yield
    stdout = run_cli_command(["core", "stop"])
    print(stdout)


@pytest.mark.order(3)
@pytest.mark.ci
def test_start_stop_procedure(
    sample_config: types.Config,
    empty_logs: Any,
    _stop_pyra_core: Any,
) -> None:
    # stop all existing pyra core processes
    _ = run_cli_command(["core", "stop"])

    stdout_2 = run_cli_command(["core", "stop"])
    assert stdout_2.startswith("No active process to be terminated")

    stdout_3 = run_cli_command(["core", "is-running"])
    assert stdout_3.startswith("pyra-core is not running")

    # make sure, the info logs are empty
    if os.path.isfile(DEBUG_LOG_PATH):
        os.remove(DEBUG_LOG_PATH)
    time.sleep(0.2)

    stdout_4 = run_cli_command(["core", "start"])
    assert stdout_4.startswith("Started background process with process ID")

    pid_string = (
        stdout_4.replace("Started background process with process ID", "")
        .replace("\n", "")
        .replace(" ", "")
        .replace("\r", "")
        .replace("\t", "")
    )
    assert pid_string.isnumeric()
    pid = int(pid_string)

    time.sleep(5)

    with open(DEBUG_LOG_PATH, "r") as f:
        actual_log_lines = f.read()
    assert (
        f"main - INFO - Starting mainloop inside process with process ID {pid}" in actual_log_lines
    )
    assert "main - DEBUG - Finished iteration" in actual_log_lines

    stdout_5 = run_cli_command(["core", "is-running"])
    assert stdout_5.startswith(f"pyra-core is running with process ID(s) [{pid}]")

    stdout_6 = run_cli_command(["core", "stop"])
    assert stdout_6.startswith(
        f"Terminated 1 pyra-core background processe(s) with process ID(s) [{pid}]"
    )

    stdout_7 = run_cli_command(["core", "is-running"])
    assert stdout_7.startswith("pyra-core is not running")
