import datetime
import subprocess
import os
import sys
import time
from packages.core import types
from typing import Any
import pytest
from ..fixtures import sample_config, empty_logs

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
INTERPRETER_PATH = sys.executable
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


@pytest.fixture()
def _stop_pyra_core() -> Any:
    yield
    stdout = run_cli_command(["core", "stop"])


@pytest.mark.order(3)
@pytest.mark.ci
def test_start_stop_procedure(
    sample_config: types.Config,
    empty_logs: Any,
    _stop_pyra_core: Any,
) -> None:
    now = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=2)

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
    )
    assert pid_string.isnumeric()
    pid = int(pid_string)

    time.sleep(5)

    with open(DEBUG_LOG_PATH, "r") as f:
        actual_log_lines = f.read()
    assert actual_log_lines.count("\n") >= 5

    print(f"actual log lines:\n{actual_log_lines}\n")
    # fmt: off
    expected_lines = [
        'cli - INFO - running command "core start"',
        # main
        f"main - INFO - Starting mainloop inside process with process ID {pid}",
        "main - INFO - Loading astronomical dataset",
        "main - INFO - Initializing threads",
        "main - INFO - Removing temporary state from previous runs",
        "main - INFO - Established graceful teardown hook",
        "main - DEBUG - Starting iteration",
        "main - DEBUG - pyra-core in test mode",
        "main - DEBUG - Finished iteration",
        "main - DEBUG - Waiting 29.",
        # threads
        "camtracker-thread - DEBUG - Thread is pausing",
        "cas-thread - DEBUG - Starting the thread",
        "helios-thread - DEBUG - Thread is pausing",
        "opus-thread - DEBUG - Starting the thread",
        "system-monitor-thread - DEBUG - Starting the thread",
        "tum-enclosure-thread - DEBUG - Thread is pausing",
        "upload-thread - DEBUG - Thread is pausing",
        # cas
        "cas - INFO - Starting Condition Assessment System (CAS) thread.",
        "cas - DEBUG - Starting iteration",
        "cas - DEBUG - Coordinates used from CamTracker (lat, lon, alt): (48.151, 11.569, 539).",
        "cas - INFO - Decision mode for measurements is: automatic.",
        "cas - DEBUG - Evaluating automatic decision",
        "cas - INFO - Measurements should be running is set to: ",
        "cas - DEBUG - Sleeping 29.",
        # opus
        "opus - INFO - Starting OPUS thread",
        "opus - INFO - OPUS thread is skipped in test mode",
    ]
    # fmt: on
    for expected_line in expected_lines:
        assert any(
            [
                " - ".join(l.split(" - ")[1:]).startswith(expected_line)
                for l in actual_log_lines.split("\n")
                if len(l.split(" - ")) > 1
            ]
        ), f"Could not find the expected log line: {expected_line}"

    parsed_line_times: int = 0
    for line in actual_log_lines.split("\n"):
        try:
            line_time = datetime.datetime.strptime(
                line.split(" - ")[0], "%Y-%m-%d %H:%M:%S.%f UTC%z"
            ).astimezone(datetime.timezone.utc)
            parsed_line_times += 1
            assert (line_time >= now) and ((now - line_time).total_seconds() < 12)
            assert line_time >= now
        except ValueError as e:
            continue

    assert parsed_line_times >= 5, "Could not parse the timestamps of the log lines"

    stdout_5 = run_cli_command(["core", "is-running"])
    assert stdout_5.startswith(f"pyra-core is running with process ID(s) [{pid}]")

    stdout_6 = run_cli_command(["core", "stop"])
    assert stdout_6.startswith(
        f"Terminated 1 pyra-core background processe(s) with process ID(s) [{pid}]"
    )

    stdout_7 = run_cli_command(["core", "is-running"])
    assert stdout_7.startswith("pyra-core is not running")
