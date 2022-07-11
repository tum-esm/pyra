from datetime import datetime
import subprocess
import os
import time
from ..fixtures import original_config, original_logs

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
INFO_LOG_PATH = os.path.join(PROJECT_DIR, "logs", "info.log")


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


def test_start_stop_procedure(original_config, original_logs):
    # terminate all pyra-core processes
    run_cli_command(["core", "stop"])

    stdout_2 = run_cli_command(["core", "stop"])
    assert stdout_2.startswith("No active process to be terminated")

    stdout_3 = run_cli_command(["core", "is-running"])
    assert stdout_3.startswith("pyra-core is not running")

    # make sure, the info logs are empty
    with open(INFO_LOG_PATH, "w"):
        pass

    stdout_4 = run_cli_command(["core", "start"])
    assert stdout_4.startswith("Started background process with PID")

    pid_string = (
        stdout_4.replace("Started background process with PID", "")
        .replace("\n", "")
        .replace(" ", "")
    )
    assert pid_string.isnumeric()
    pid = int(pid_string)

    time.sleep(1)

    with open(INFO_LOG_PATH, "r") as f:
        info_log_lines = f.readlines()
    assert len(info_log_lines) >= 3

    print("first three log lines:\n" + "".join(info_log_lines[:3]) + "\n")
    expected_lines = [
        f"main - INFO - started mainloop inside process with PID {pid}",
        "main - INFO - Starting Iteration",
        "main - INFO - pyra-core in test mode",
    ]
    now = datetime.utcnow()
    for expected_line, actual_line in zip(expected_lines, info_log_lines[:3]):
        line_time = datetime.strptime(actual_line[:19], "%Y-%m-%d %H:%M:%S")

        print(f"expected log line: {'.'*29}{expected_line}")
        print(f"actual log line:   {actual_line}\n")
        assert (now - line_time).total_seconds() < 3
        assert actual_line.endswith(expected_line + "\n")

    stdout_5 = run_cli_command(["core", "is-running"])
    assert stdout_5.startswith(f"pyra-core is running with PID {pid}")

    stdout_6 = run_cli_command(["core", "stop"])
    assert stdout_6.startswith(f"Terminated 1 background processe(s) with PID(s) [{pid}]")

    stdout_7 = run_cli_command(["core", "is-running"])
    assert stdout_7.startswith("pyra-core is not running")
