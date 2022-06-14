import json
import subprocess
import click
import os

import psutil

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "run-pyra-core.py")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


def process_is_running():
    for p in psutil.process_iter():
        try:
            arguments = p.cmdline()
            if (len(arguments) > 0) and (arguments[-1] == SCRIPT_PATH):
                return p.pid
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            pass
    return None


def terminate_processes():
    termination_pids = []
    for p in psutil.process_iter():
        try:
            arguments = p.cmdline()
            if (len(arguments) > 0) and (arguments[-1] == SCRIPT_PATH):
                termination_pids.append(p.pid)
                p.terminate()
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            pass
    return termination_pids


@click.command(
    help="Start pyra-core as a background process. "
    + "Prevents spawning multiple processes"
)
def _start_pyra_core():
    existing_pid = process_is_running()
    if existing_pid is not None:
        error_handler(f"Background process already exists with PID {existing_pid}")
    else:
        p = subprocess.Popen(
            [INTERPRETER_PATH, SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        success_handler(f"Started background process with PID {p.pid}")


@click.command(help="Stop the pyra-core background process")
def _stop_pyra_core():
    termination_pids = terminate_processes()
    if len(termination_pids) == 0:
        error_handler("No active process to be terminated")
    else:
        success_handler(
            f"Terminated {len(termination_pids)} background "
            + f"processe(s) with PID(s) {termination_pids}"
        )


@click.command(help="Checks whether the pyra-core background process is running")
def _pyra_core_is_running():
    existing_pid = process_is_running()
    if existing_pid is not None:
        success_handler(f"pyra-core is running with PID {existing_pid}")
    else:
        error_handler("pyra-core is not running")


@click.group()
def core_command_group():
    pass


core_command_group.add_command(_start_pyra_core, name="start")
core_command_group.add_command(_stop_pyra_core, name="stop")
core_command_group.add_command(_pyra_core_is_running, name="is-running")
