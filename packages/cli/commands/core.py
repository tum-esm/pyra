"""Start and stop the pyra-core background process."""

import os
import subprocess
import sys

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

logger = utils.Logger(origin="cli")


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
    with interfaces.StateInterface.update_state() as s:
        s.activity.cli_calls += 1
    logger.info('running command "core start"')

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
    with interfaces.StateInterface.update_state() as s:
        s.activity.cli_calls += 1
    logger.info('running command "core stop"')

    termination_pids = tum_esm_utils.processes.terminate_process(
        _RUN_PYRA_CORE_SCRIPT_PATH,
        termination_timeout=8,
    )
    if len(termination_pids) == 0:
        _print_red("No active process to be terminated")
        exit(0)

    _print_green(
        f"Terminated {len(termination_pids)} pyra-core background "
        + f"processe(s) with process ID(s) {termination_pids}"
    )

    config = types.Config.load(ignore_path_existence=True)
    state = interfaces.StateInterface.load_state()

    if config.general.test_mode:
        _print_green("Skip closing Enlosure, CamTracker, and OPUS teardown in test mode")
        exit(0)

    if config.tum_enclosure is not None:
        _print_green("Running teardown for TUM enclosure")
        current_cover_angle = (
            interfaces.StateInterface.load_state().tum_enclosure_state.actors.current_angle
        )
        if current_cover_angle == 0:
            _print_green("Cover is already closed")
        else:
            try:
                click.echo("Closing cover")
                threads.TUMEnclosureThread.force_cover_close(config, logger)
                _print_green("Successfully closed cover")
            except Exception as e:
                _print_red(f"Failed to close cover: {e}")
                exit(1)

    camtracker_logger = utils.Logger(origin="camtracker")
    try:
        if threads.camtracker_thread.CamTrackerProgram.is_running():
            threads.camtracker_thread.CamTrackerProgram.stop(config, camtracker_logger)
        _print_green("Successfully closed CamTracker")
    except Exception as e:
        _print_red(f"Failed to close CamTracker: {e}")
        exit(1)

    opus_logger = utils.Logger(origin="opus")
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

        # check whether the following 3 log lines are at the end of the current log file
        # crop 38 chars at the beginning of each line ("2025-01-13 22:45:01.756072 UTC+0100 - ")
        expected_log_lines = [
            'cli - INFO - running command "core stop"',
            "main - INFO - Received shutdown signal, starting graceful teardown",
            "main - INFO - Graceful teardown complete",
        ]
        logs_archive_path = os.path.join(_PROJECT_DIR, "logs", "archive")
        log_files = [f for f in sorted(os.listdir(logs_archive_path)) if f.endswith("-debug.log")]
        if len(log_files) == 0:
            return
        latest_log_file_path = os.path.join(logs_archive_path, log_files[-1])
        latest_log_lines = [
            (l[38:] if len(l) > 38 else l)
            for l in tum_esm_utils.files.load_file(latest_log_file_path).strip("\n\t ").split("\n")
        ]
        if len(latest_log_lines) < 20:
            return

        # if not properly shut down, raise an exception and send an email
        for el in expected_log_lines:
            if el not in latest_log_lines[-20:]:
                _print_red("pyra-core is not running")
                _print_red(
                    f"Pyra Core has not been shut down properly. Expected log line '{el}' not found in the last 20 lines of {latest_log_file_path}"
                )

                new_exception_state_item = types.ExceptionStateItem(
                    origin="cli",
                    subject="PyraCoreNotRunning",
                    details="Pyra Core has not been shut down properly.",
                    send_emails=True,
                )
                with interfaces.StateInterface.update_state() as s:
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
