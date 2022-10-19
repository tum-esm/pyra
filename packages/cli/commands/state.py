import json
import click
import os
from packages.core import utils, interfaces

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")


@click.command(help="Read the current state.json file.")
@click.option("--indent", is_flag=True, help="Print the JSON in an indented manner")
@utils.with_filelock(STATE_LOCK_PATH)
def _get_state(indent: bool) -> None:
    if not os.path.isfile(STATE_FILE_PATH):
        interfaces.StateInterface.initialize()

    with open(STATE_FILE_PATH, "r") as f:
        try:
            state_content = json.load(f)
        except:
            raise AssertionError("file not in a valid json format")

    click.echo(json.dumps(state_content, indent=(2 if indent else None)))


@click.group()
def state_command_group() -> None:
    pass


state_command_group.add_command(_get_state, name="get")
