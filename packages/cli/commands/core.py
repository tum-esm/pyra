import json
import subprocess
import click
import os

import psutil

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
PROCESS_STATE_FILE = os.path.join(PROJECT_DIR, "pyra-core-process-state.json")

INTERPRETER_PATH = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "run-pyra-core.py")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


@click.command(
    help="Start pyra-core as a background process. "
    + "Prevents spawning multiple processes"
)
def _start_pyra_core():
    if os.path.isfile(PROCESS_STATE_FILE):
        error_handler("Background process already exists")
    else:
        p = subprocess.Popen([INTERPRETER_PATH, SCRIPT_PATH])
        success_handler(f"Started pyra-core with PID {p.pid}")


@click.command(help="Stop the pyra-core background process")
def _stop_pyra_core():
    if not os.path.isfile(PROCESS_STATE_FILE):
        error_handler("No background process found")
    else:
        try:
            with open(PROCESS_STATE_FILE, "r") as f:
                pid = json.load(f)["pid"]
            try:
                psutil.Process(pid).terminate()
                success_handler(f"Terminated background process with PID {pid}")
            except psutil.NoSuchProcess:
                error_handler("Process has already been terminated")
            os.remove(PROCESS_STATE_FILE)
        except Exception as e:
            error_handler(f"Could not terminate background process: {e}")


@click.command(help="Checks whether the pyra-core background process is running")
def _pyra_core_is_running():
    try:
        with open(PROCESS_STATE_FILE, "r") as f:
            pid = json.load(f)["pid"]
        assert psutil.Process(pid).status() == psutil.STATUS_RUNNING
        success_handler(f"pyra-core is running with PID {pid}")
    except:
        error_handler("pyra-core is not running")


@click.group()
def core_command_group():
    pass


core_command_group.add_command(_start_pyra_core, name="start")
core_command_group.add_command(_stop_pyra_core, name="stop")
core_command_group.add_command(_pyra_core_is_running, name="is-running")
