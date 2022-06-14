import json
import click
import os
import sys
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "runtime-data", ".state.lock")


sys.path.append(PROJECT_DIR)
from packages.core.utils import Validation

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))
Validation.logging_handler = error_handler

# FileLock = Mark, that the config JSONs are being used and the
# CLI should not interfere. A file "config/config.lock" will be created
# and the existence of this file will make the next line wait.
def with_filelock(function):
    def locked_function(*args, **kwargs):
        with filelock.FileLock(STATE_LOCK_PATH):
            return function(*args, **kwargs)

    return locked_function


@click.command(help="Read the current state.json file.")
@click.option(
    "--no-indent", is_flag=True, help="Do not print the JSON in an indented manner"
)
@with_filelock
def _get_state(no_indent):
    try:
        assert os.path.isfile(STATE_FILE_PATH), "pyra-core is not running"
        with open(STATE_FILE_PATH, "r") as f:
            try:
                content = json.load(f)
                assert isinstance(content, dict)
                assert isinstance(content["automation_should_be_running"], bool)
                assert isinstance(content["enclosure_plc_readings"], list)
            except:
                raise AssertionError("file not in a valid json format")

        if len(content["enclosure_plc_readings"]) == 17:
            plc_state = content["enclosure_plc_readings"]
        else:
            plc_state = [None] * 17
        content = {
            "automation_should_be_running": content["automation_should_be_running"],
            "enclosure_plc_readings": {
                "actors": {"fan_speed": plc_state[0], "current_angle": plc_state[1]},
                "control": {
                    "auto_temp_mode": plc_state[2],
                    "manual_control": plc_state[3],
                    "manual_temp_mode": plc_state[4],
                },
                "sensors": {"humidity": plc_state[5], "temperature": plc_state[6]},
                "state": {
                    "camera": plc_state[7],
                    "computer": plc_state[8],
                    "cover_closed": plc_state[9],
                    "heater": plc_state[10],
                    "motor_failed": plc_state[11],
                    "rain": plc_state[12],
                    "reset_needed": plc_state[13],
                    "router": plc_state[14],
                    "spectrometer": plc_state[15],
                    "ups_alert": plc_state[16],
                },
            },
        }
        click.echo(json.dumps(content, indent=(None if no_indent else 2)))
    except AssertionError as e:
        error_handler(e)


@click.group()
def state_command_group():
    pass


state_command_group.add_command(_get_state, name="get")
