import subprocess
import os
import time
from pathlib import Path
from unittest.mock import Mock

from click.testing import CliRunner
from packages.cli.commands import core
from packages.core import types
from typing import Any
import pytest
from ..fixtures import sample_config, empty_logs  # pyright: ignore[reportUnusedImport]

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
PYRA_CLI_PATH = os.path.join(PROJECT_DIR, "packages", "cli", "main.py")
DEBUG_LOG_PATH = os.path.join(PROJECT_DIR, "logs", "debug.log")


def run_cli_command(command: list[str]) -> str:
    """Run a CLI command, print its output, and return stdout after a successful exit."""
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
    """Stop Core after the test to clean up any background process it started."""
    yield
    stdout = run_cli_command(["core", "stop"])
    print(stdout)


@pytest.mark.ci
@pytest.mark.parametrize("crashed", [False, True])
def test_is_running_checks_latest_core_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, crashed: bool
) -> None:
    """Check that an earlier clean shutdown cannot mask a crash in the latest run."""
    archive = tmp_path / "logs" / "archive"
    archive.mkdir(parents=True)
    timestamps = "2026-01-01 12:00:00.000000 UTC+0000 - "
    startup = "main - INFO - Starting mainloop inside process with process ID 100"
    stop = 'lifecycle - INFO - running command "core stop"'
    messages = [startup, stop]
    if crashed:
        messages.append(startup.replace("100", "101"))
    (archive / "2026-01-01-debug.log").write_text(
        "".join(f"{timestamps}{message}\n" for message in messages)
    )
    monkeypatch.setattr(core, "_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(core.logger, "debug", Mock())
    monkeypatch.setattr(core.tum_esm_utils.processes, "get_process_pids", Mock(return_value=[]))
    monkeypatch.setattr(core.tum_esm_utils.sqlitelock, "SQLiteLock", Mock())
    reporter = Mock()
    monkeypatch.setattr(core.interfaces, "ExceptionsInterface", reporter)
    config_load = Mock()
    monkeypatch.setattr(core.types.Config, "load", config_load)

    result = CliRunner().invoke(core.core_command_group, ["is-running"])

    assert result.exit_code == 0
    assert result.output.startswith("pyra-core is not running")
    if crashed:
        reporter.return_value.add_exception.assert_called_once_with(
            "cli", types.KNOWN_EXCEPTIONS.PYRA_CORE_CRASHED
        )
        config_load.assert_called_once_with(ignore_path_existence=True)
        reporter.update_exception_notifications.assert_called_once()
    else:
        reporter.assert_not_called()


@pytest.mark.order(3)
@pytest.mark.ci
def test_start_stop_procedure(
    sample_config: types.Config,
    empty_logs: Any,
    _stop_pyra_core: Any,
) -> None:
    """Start Core through the CLI, verify its status and logs, then stop it."""
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
