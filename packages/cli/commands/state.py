import json
import click
import os
from packages.core.utils import StateInterface, with_filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")


@click.command(help="Read the current state.json file.")
@click.option("--no-indent", is_flag=True, help="Do not print the JSON in an indented manner")
@with_filelock(STATE_LOCK_PATH)
def _get_state(no_indent: bool) -> None:
    if not os.path.isfile(STATE_FILE_PATH):
        StateInterface.initialize()

    with open(STATE_FILE_PATH, "r") as f:
        try:
            state_content = json.load(f)
            assert isinstance(state_content, dict)
            assert isinstance(state_content["measurements_should_be_running"], bool)
            assert isinstance(state_content["enclosure_plc_readings"], dict)
            assert isinstance(state_content["os_state"], dict)
        except:
            raise AssertionError("file not in a valid json format")

    click.echo(json.dumps(state_content, indent=(None if no_indent else 2)))


@click.group()
def state_command_group() -> None:
    pass


state_command_group.add_command(_get_state, name="get")
