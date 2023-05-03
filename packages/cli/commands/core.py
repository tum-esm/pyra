"""Start and stop the pyra-core background process."""

import subprocess
from typing import Optional
import click
import os
import filelock
import psutil
import tum_esm_utils
from packages.core import utils, interfaces, modules

dir = os.path.dirname
_PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
_INTERPRETER_PATH = (
    "python" if os.name != "posix" else os.path.join(_PROJECT_DIR, ".venv", "bin", "python")
)
_CORE_SCRIPT_PATH = os.path.join(_PROJECT_DIR, "run_pyra_core.py")

_run_pyra_core_lock = filelock.FileLock(
    os.path.join(
        tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=5),
        "run_pyra_core.lock",
    ),
    timeout=0.5,
)


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


# TODO: use tum_esm_utils


def _process_is_running() -> Optional[int]:
    for p in psutil.process_iter():
        try:
            arguments = p.cmdline()
            if (len(arguments) == 2) and (arguments[1] == _CORE_SCRIPT_PATH):
                return p.pid
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            pass
    return None


# TODO: use tum_esm_utils


def _terminate_processes() -> list[int]:
    termination_pids: list[int] = []
    for p in psutil.process_iter():
        try:
            arguments = p.cmdline()
            if len(arguments) > 0:
                if arguments[-1] == _CORE_SCRIPT_PATH:
                    termination_pids.append(p.pid)
                    p.terminate()
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            pass
    return termination_pids


@click.command(
    help="Start pyra-core as a background process. Return the process id. Prevents spawning multiple processes."
)
def _start_pyra_core() -> None:
    existing_pid = _process_is_running()
    if existing_pid is not None:
        _print_red(f"Background process already exists with PID {existing_pid}")
        return

    try:
        _run_pyra_core_lock.acquire()
        _run_pyra_core_lock.release()
    except filelock.Timeout:
        _print_red("PyraCore process already exists with unknown PID")
        return

    p = subprocess.Popen(
        [_INTERPRETER_PATH, _CORE_SCRIPT_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    utils.Logger.log_activity_event("start-core")
    _print_green(f"Started background process with PID {p.pid}")


@click.command(
    help="Stop the pyra-core background process. Return the process id of terminated processes. This command will force quit the OPUS process."
)
def _stop_pyra_core() -> None:
    termination_pids = _terminate_processes()
    if len(termination_pids) == 0:
        _print_red("No active process to be terminated")
    else:
        _print_green(
            f"Terminated {len(termination_pids)} pyra-core background "
            + f"processe(s) with PID(s) {termination_pids}"
        )
        utils.Logger.log_activity_event("stop-core")

        config = interfaces.ConfigInterface.read()
        if config["general"]["test_mode"]:
            _print_green("Skipping TUM_PLC, CamTracker, and OPUS in test mode")
            return

        config = interfaces.ConfigInterface().read()

        if config["tum_plc"] is not None:
            try:
                enclosure = modules.enclosure_control.EnclosureControl(config)
                enclosure.force_cover_close()
                enclosure.plc_interface.disconnect()
                _print_green("Successfully closed cover")
            except Exception as e:
                _print_red(f"Failed to close cover: {e}")

        try:
            tracking = modules.sun_tracking.SunTracking(config)
            if tracking.ct_application_running():
                tracking.stop_sun_tracking_automation()
            _print_green("Successfully closed CamTracker")
        except Exception as e:
            _print_red(f"Failed to close CamTracker: {e}")

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


@click.command(help="Checks whether the pyra-core background process is running.")
def _pyra_core_is_running() -> None:
    existing_pid = _process_is_running()
    if existing_pid is not None:
        _print_green(f"pyra-core is running with PID {existing_pid}")
    else:
        _print_red("pyra-core is not running")


@click.group()
def core_command_group() -> None:
    pass


core_command_group.add_command(_start_pyra_core, name="start")
core_command_group.add_command(_stop_pyra_core, name="stop")
core_command_group.add_command(_pyra_core_is_running, name="is-running")
