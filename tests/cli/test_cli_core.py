from datetime import datetime
import subprocess
import os
import time
from packages.core import types
from typing import Any
import pytest
from ..fixtures import sample_config, empty_logs

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
DEBUG_LOG_PATH = os.path.join(PROJECT_DIR, "logs", "debug.log")


def run_cli_command(command: list[str]) -> str:
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


@pytest.mark.ci
def test_start_stop_procedure(
    sample_config: types.Config, empty_logs: Any
) -> None:
    # terminate all pyra-core processes
    run_cli_command(["core", "stop"])

    stdout_2 = run_cli_command(["core", "stop"])
    assert stdout_2.startswith("No active process to be terminated")

    stdout_3 = run_cli_command(["core", "is-running"])
    assert stdout_3.startswith("pyra-core is not running")

    # make sure, the info logs are empty
    if os.path.isfile(DEBUG_LOG_PATH):
        os.remove(DEBUG_LOG_PATH)

    stdout_4 = run_cli_command(["core", "start"])
    assert stdout_4.startswith("Started background process with process ID")

    pid_string = (
        stdout_4.replace("Started background process with process ID",
                         "").replace("\n", "").replace(" ", "")
    )
    assert pid_string.isnumeric()
    pid = int(pid_string)

    time.sleep(8)

    with open(DEBUG_LOG_PATH, "r") as f:
        actual_log_lines = f.read()
    assert actual_log_lines.count("\n") >= 5

    print(f"actual log lines:\n{actual_log_lines}\n")
    expected_lines = [
        f"main - INFO - Starting mainloop inside process with process ID {pid}",
        "main - INFO - Loading astronomical dataset",
        "main - INFO - Initializing mainloop modules",
        "main - INFO - Initializing threads",
        "main - INFO - Starting iteration",
        "main - INFO - pyra-core in test mode",
    ]
    now = datetime.utcnow()
    for expected_line in expected_lines:
        assert expected_line in actual_log_lines

    parsed_line_times: int = 0
    for line in actual_log_lines.split("\n"):
        try:
            line_time = datetime.strptime(
                line.split(" - ")[0][: 19], "%Y-%m-%d %H:%M:%S"
            )
            parsed_line_times += 1
            assert (now - line_time).total_seconds() < 12
        except ValueError:
            continue

    assert parsed_line_times >= 5, "Could not parse the timestamps of the log lines"

    stdout_5 = run_cli_command(["core", "is-running"])
    assert stdout_5.startswith(
        f"pyra-core is running with process ID(s) [{pid}]"
    )

    stdout_6 = run_cli_command(["core", "stop"])
    assert stdout_6.startswith(
        f"Terminated 1 pyra-core background processe(s) with process ID(s) [{pid}]"
    )

    stdout_7 = run_cli_command(["core", "is-running"])
    assert stdout_7.startswith("pyra-core is not running")
