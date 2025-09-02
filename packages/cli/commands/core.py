"""Start and stop the pyra-core background process."""

import datetime
import os
import subprocess
import sys
from typing import Optional

import click
import filelock
import tum_esm_utils

from packages.core import interfaces, threads, types, utils

dir = os.path.dirname
_PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
_RUN_PYRA_CORE_SCRIPT_PATH = os.path.join(_PROJECT_DIR, "run_pyra_core.py")

_run_pyra_core_lock = filelock.FileLock(
    os.path.join(
        tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=5),
        "run_pyra_core.lock",
    ),
    timeout=0.5,
)

logger = utils.Logger(origin="cli", lock=None)
lifecycle_logger = utils.Logger(origin="lifecycle", lock=None)


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.group(name="core")
def core_command_group() -> None:
    pass


@core_command_group.command(
    name="start",
    help="Start pyra-core as a background process. Return the process id. Prevents spawning multiple processes.",
)
def _start_pyra_core() -> None:
    logger.info('running command "core start"')

    # so that the start/stop also appears in the core logs (not only in the cli logs)
    lifecycle_logger.info('running command "core start"')

    existing_pids = tum_esm_utils.processes.get_process_pids(_RUN_PYRA_CORE_SCRIPT_PATH)
    if len(existing_pids) > 0:
        _print_red(f"Background process already exists with process ID(s) {existing_pids}")
        exit(1)

    try:
        _run_pyra_core_lock.acquire(timeout=0.25)
        _run_pyra_core_lock.release()
    except filelock.Timeout:
        _print_red("PyraCore process already exists with unknown process ID")
        return

    p = subprocess.Popen(
        [sys.executable, _RUN_PYRA_CORE_SCRIPT_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _print_green(f"Started background process with process ID {p.pid}")

    exit(0)


@core_command_group.command(
    name="stop",
    help="Stop the pyra-core background process. Return the process id of terminated processes. This command will force quit the OPUS process.",
)
def _stop_pyra_core() -> None:
    logger.info('running command "core stop"')

    termination_pids = tum_esm_utils.processes.terminate_process(
        _RUN_PYRA_CORE_SCRIPT_PATH,
        termination_timeout=20,
    )
    if len(termination_pids) == 0:
        _print_red("No active process to be terminated")
        exit(0)

    _print_green(
        f"Terminated {len(termination_pids)} pyra-core background "
        + f"processe(s) with process ID(s) {termination_pids}"
    )

    # so that the start/stop also appears in the core logs (not only in the cli logs)
    lifecycle_logger.info('running command "core stop"')

    config = types.Config.load(ignore_path_existence=True)
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )
    state = interfaces.StateInterface.load_state(state_lock, logger)

    if config.general.test_mode:
        _print_green("Skip closing Enlosure, CamTracker, and OPUS teardown in test mode")
        exit(0)

    if config.tum_enclosure is not None:
        _print_green("Running teardown for TUM enclosure")
        current_cover_angle = state.tum_enclosure_state.actors.current_angle
        if current_cover_angle == 0:
            _print_green("Cover is already closed")
        else:
            try:
                click.echo("Closing cover")
                threads.TUMEnclosureThread.force_cover_close(config, state_lock, logger)
                _print_green("Successfully closed cover")
            except Exception as e:
                _print_red(f"Failed to close cover: {e}")
                exit(1)

    camtracker_logger = utils.Logger(origin="camtracker", lock=None)
    try:
        if threads.camtracker_thread.CamTrackerProgram.is_running():
            threads.camtracker_thread.CamTrackerProgram.stop(config, camtracker_logger)
        _print_green("Successfully closed CamTracker")
    except Exception as e:
        _print_red(f"Failed to close CamTracker: {e}")
        exit(1)

    opus_logger = utils.Logger(origin="opus", lock=None)
    try:
        if threads.opus_thread.OpusProgram.is_running(opus_logger):
            try:
                if (state.opus_state.macro_filepath is not None) and (
                    state.opus_state.macro_id is not None
                ):
                    tum_esm_utils.opus.OpusHTTPInterface.stop_macro(state.opus_state.macro_filepath)
            except Exception as e:
                _print_red(f"Failed to stop OPUS macro: {e}")
            threads.opus_thread.OpusProgram.stop(opus_logger)
            _print_green("Successfully closed OPUS")
        else:
            _print_green("OPUS is already closed")
    except Exception as e:
        _print_red(f"Failed to close OPUS: {e}")
        exit(1)

    _print_green("Successfully closed all processes, resetting temporary state")
    with interfaces.StateInterface.update_state(state_lock, logger) as s:
        s.reset()


@core_command_group.command(
    name="is-running", help="Checks whether the pyra-core background process is running."
)
def _pyra_core_is_running() -> None:
    logger.debug('running command "core is-running"')
    existing_pids = tum_esm_utils.processes.get_process_pids(_RUN_PYRA_CORE_SCRIPT_PATH)
    if len(existing_pids) > 0:
        _print_green(f"pyra-core is running with process ID(s) {existing_pids}")
    else:
        _print_red("pyra-core is not running")

        # CHECK WHETHER PYRA CORE WAS PROPERLY SHUT DOWN

        # 1. search for the latest time the core was running

        logs_archive_path = os.path.join(_PROJECT_DIR, "logs", "archive")
        logfile_names = [
            f for f in sorted(os.listdir(logs_archive_path)) if f.endswith("-debug.log")
        ]
        last_main_log_date: Optional[datetime.date] = None
        for logfile_name in logfile_names:
            last_mainlog_line: Optional[int] = None
            lines = (
                tum_esm_utils.files.load_file(os.path.join(logs_archive_path, logfile_name))
                .strip("\n\t ")
                .split("\n")
            )
            for i, line in list(enumerate(lines))[::-1]:
                if "main - INFO - " in line:
                    last_mainlog_line = i

            if last_mainlog_line is not None:
                try:
                    last_main_log_date = datetime.datetime.strptime(
                        logfile_name[:10], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    pass
        if last_main_log_date is None:
            _print_red("core has never run before")
            return

        # 2. load the three log files around that date (date and date ± 1 day)

        log_lines: list[str] = []
        for offset in [-1, 0, 1]:
            logfile_path = os.path.join(
                logs_archive_path,
                (last_main_log_date + datetime.timedelta(days=offset)).strftime(
                    "%Y-%m-%d-debug.log"
                ),
            )
            if os.path.exists(logfile_path):
                log_lines += tum_esm_utils.files.load_file(logfile_path).strip("\t\n ").split("\n")

        # 3. only consider the log lines ± 200 lines around the last core activity

        last_mainlog_index: Optional[int] = None
        for i, line in list(enumerate(log_lines))[::-1]:
            if "main - INFO - " in line:
                last_mainlog_index = i
                break
        assert last_mainlog_index is not None

        from_log_line_index = last_mainlog_index - 200
        to_log_line_index = last_mainlog_index + 200
        if from_log_line_index < 0:
            from_log_line_index = 0
        if to_log_line_index >= len(log_lines):
            to_log_line_index = len(log_lines) - 1
        log_lines = log_lines[from_log_line_index:to_log_line_index]

        # 4. Check whether core has been stopped properly

        if 'lifecycle - INFO - running command "core stop"' not in "\n".join(log_lines):
            _print_red(f"Pyra Core has not been shut down properly")
            state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
                filepath=interfaces.state_interface.STATE_LOCK_PATH,
                timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
                poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
            )
            new_exception_state_item = types.ExceptionStateItem(
                origin="cli",
                subject="PyraCoreNotRunning",
                details="Pyra Core has not been shut down properly.",
                send_emails=True,
            )
            with interfaces.StateInterface.update_state(state_lock, logger) as s:
                if new_exception_state_item not in s.exceptions_state.current:
                    _print_red("exception not raised yet, loading config")
                    config = types.Config.load()
                    utils.ExceptionEmailClient.handle_occured_exceptions(
                        config, [new_exception_state_item]
                    )
                    s.exceptions_state.current.append(new_exception_state_item)
                    s.exceptions_state.notified.append(new_exception_state_item)
                else:
                    _print_red("exception already raised")

            return
