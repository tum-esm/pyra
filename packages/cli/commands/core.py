"""Start and stop the pyra-core background process."""

import subprocess
import sys
import click
import os
import filelock
import psutil
import tum_esm_utils
from packages.core import interfaces, modules, types, utils

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
    interfaces.StateInterface.update_state(recent_cli_calls=1)
    logger.info('running command "core start"')

    existing_pids = tum_esm_utils.processes.get_process_pids(
        _RUN_PYRA_CORE_SCRIPT_PATH
    )
    if len(existing_pids) > 0:
        _print_red(
            f"Background process already exists with process ID(s) {existing_pids}"
        )
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
    interfaces.StateInterface.update_state(recent_cli_calls=1)
    logger.info('running command "core stop"')

    termination_pids = tum_esm_utils.processes.terminate_process(
        _RUN_PYRA_CORE_SCRIPT_PATH
    )
    if len(termination_pids) == 0:
        _print_red("No active process to be terminated")
        exit(0)

    _print_green(
        f"Terminated {len(termination_pids)} pyra-core background " +
        f"processe(s) with process ID(s) {termination_pids}"
    )

    config = types.Config.load(ignore_path_existence=True)
    if config.general.test_mode:
        _print_green("Skip closing TUM_PLC, CamTracker, and OPUS in test mode")
        exit(0)

    if config.tum_plc is not None:
        try:
            enclosure = modules.enclosure_control.EnclosureControl(config)
            enclosure.force_cover_close()
            enclosure.plc_interface.disconnect()
            _print_green("Successfully closed cover")
        except Exception as e:
            _print_red(f"Failed to close cover: {e}")
            exit(1)

    try:
        tracking = modules.sun_tracking.SunTracking(config)
        if tracking.ct_application_running():
            tracking.stop_sun_tracking_automation()
        _print_green("Successfully closed CamTracker")
    except Exception as e:
        _print_red(f"Failed to close CamTracker: {e}")
        exit(1)

    try:
        processes = [p.name() for p in psutil.process_iter()]
        for executable in ["opus.exe", "OpusCore.exe"]:
            if executable in processes:
                exit_code = os.system(f"taskkill /f /im {executable}")
                assert (
                    exit_code == 0
                ), f'taskkill  of "{executable}" ended with an exit_code of {exit_code}'
        _print_green("Successfully closed OPUS")
    except Exception as e:
        _print_red(f"Failed to close OPUS: {e}")
        exit(1)


@core_command_group.command(
    name="is-running",
    help="Checks whether the pyra-core background process is running."
)
def _pyra_core_is_running() -> None:
    logger.info('running command "core is-running"')
    existing_pids = tum_esm_utils.processes.get_process_pids(
        _RUN_PYRA_CORE_SCRIPT_PATH
    )
    if len(existing_pids) > 0:
        _print_green(f"pyra-core is running with process ID(s) {existing_pids}")
    else:
        _print_red("pyra-core is not running")
