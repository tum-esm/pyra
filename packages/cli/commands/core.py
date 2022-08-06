import subprocess
import time
import click
import os
import psutil
from packages.core.modules.enclosure_control import EnclosureControl
from packages.core.modules.opus_measurement import OpusMeasurement
from packages.core.modules.sun_tracking import SunTracking
from packages.core.utils import ConfigInterface, Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INTERPRETER_PATH = (
    "python" if os.name != "posix" else os.path.join(PROJECT_DIR, ".venv", "bin", "python")
)
CORE_SCRIPT_PATH = os.path.join(PROJECT_DIR, "run-pyra-core.py")
SERVER_SCRIPT_PATH = os.path.join(PROJECT_DIR, "packages", "server", "main.py")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


def process_is_running():
    for p in psutil.process_iter():
        try:
            arguments = p.cmdline()
            if (len(arguments) == 2) and (arguments[1] == CORE_SCRIPT_PATH):
                return p.pid
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            pass
    return None


def terminate_processes():
    termination_pids = []
    for p in psutil.process_iter():
        try:
            arguments = p.cmdline()
            if len(arguments) > 0:
                if arguments[-1] == CORE_SCRIPT_PATH:
                    termination_pids.append(p.pid)
                    p.terminate()
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            pass
    return termination_pids


@click.command(
    help="Start pyra-core as a background process. " + "Prevents spawning multiple processes"
)
def _start_pyra_core():
    existing_pid = process_is_running()
    if existing_pid is not None:
        error_handler(f"Background process already exists with PID {existing_pid}")
    else:
        p = subprocess.Popen(
            [INTERPRETER_PATH, CORE_SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        Logger.log_activity_event("start-core")
        success_handler(f"Started background process with PID {p.pid}")


@click.command(help="Stop the pyra-core background process")
def _stop_pyra_core():
    termination_pids = terminate_processes()
    if len(termination_pids) == 0:
        error_handler("No active process to be terminated")
    else:
        success_handler(
            f"Terminated {len(termination_pids)} pyra-core background "
            + f"processe(s) with PID(s) {termination_pids}"
        )
        Logger.log_activity_event("stop-core")

        config = ConfigInterface.read()
        if config["general"]["test_mode"] or (config["tum_plc"] is None):
            return

        config = ConfigInterface().read()

        try:
            enclosure = EnclosureControl(config)
            enclosure.plc_interface.connect()
            enclosure.force_cover_close()
            enclosure.plc_interface.disconnect()
            success_handler("Successfully closed cover")
        except Exception as e:
            error_handler(f"Failed to close cover: {e}")

        try:
            tracking = SunTracking(config)
            if tracking.ct_application_running():
                tracking.stop_sun_tracking_automation()
            success_handler("Successfully closed CamTracker")
        except Exception as e:
            error_handler(f"Failed to close CamTracker: {e}")

        try:
            # TODO: kill macro forcefully
            opus = OpusMeasurement(config)
            if opus.opus_application_running():
                opus.stop_macro()
                time.sleep(2)
                opus.close_opus()
            success_handler("Successfully closed OPUS")
        except Exception as e:
            error_handler(f"Failed to close OPUS: {e}")


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
