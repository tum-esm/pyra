"""Start and stop the pyra-core background process."""

import subprocess
import sys
import click
import os
import filelock
import tum_esm_utils
from packages.core import interfaces, types, utils, threads

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
    help=
    "Start pyra-core as a background process. Return the process id. Prevents spawning multiple processes."
)
def _start_pyra_core() -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
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
    help=
    "Stop the pyra-core background process. Return the process id of terminated processes. This command will force quit the OPUS process."
)
def _stop_pyra_core() -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info('running command "core stop"')

    termination_pids = tum_esm_utils.processes.terminate_process(
        _RUN_PYRA_CORE_SCRIPT_PATH,
        termination_timeout=8,
    )
    if len(termination_pids) == 0:
        _print_red("No active process to be terminated")
        exit(0)

    _print_green(
        f"Terminated {len(termination_pids)} pyra-core background " +
        f"processe(s) with process ID(s) {termination_pids}"
    )

    config = types.Config.load(ignore_path_existence=True)
    state = interfaces.StateInterface.load_state()

    if config.general.test_mode:
        _print_green("Skip closing Enlosure, CamTracker, and OPUS teardown in test mode")
        exit(0)

    if config.tum_enclosure is not None:
        _print_green("Running teardown for TUM enclosure")
        current_cover_angle = interfaces.StateInterface.load_state(
        ).tum_enclosure_state.actors.current_angle
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
        if threads.camtracker_thread.CamTrackerProgram.is_running(camtracker_logger):
            threads.camtracker_thread.CamTrackerProgram.stop(config, camtracker_logger)
        _print_green("Successfully closed CamTracker")
    except Exception as e:
        _print_red(f"Failed to close CamTracker: {e}")
        exit(1)

    opus_logger = utils.Logger(origin="opus")
    try:
        if threads.opus_thread.OpusProgram.is_running(opus_logger):
            dde_connection = threads.opus_thread.DDEConnection(opus_logger)
            if ((state.opus_state.macro_filepath is not None) and
                (state.opus_state.macro_id is not None)):
                dde_connection.stop_macro(
                    state.opus_state.macro_filepath, state.opus_state.macro_id
                )
            threads.opus_thread.OpusProgram.stop(opus_logger, dde_connection)
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
    logger.info('running command "core is-running"')
    existing_pids = tum_esm_utils.processes.get_process_pids(_RUN_PYRA_CORE_SCRIPT_PATH)
    if len(existing_pids) > 0:
        _print_green(f"pyra-core is running with process ID(s) {existing_pids}")
    else:
        _print_red("pyra-core is not running")
