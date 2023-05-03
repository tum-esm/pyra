"""Read the current state.json file."""

import json
import click
import os

import tum_esm_utils
from packages.core import utils, interfaces

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "runtime-data", "state.json")
_STATE_LOCK_PATH = os.path.join(_PROJECT_DIR, "config", ".state.lock")


@click.command(help="Read the current state.json file.")
@click.option("--indent", is_flag=True, help="Print the JSON in an indented manner")
@tum_esm_utils.decorators.with_filelock(
    lockfile_path=_STATE_LOCK_PATH,
    timeout=5,
)
def _get_state(indent: bool) -> None:
    if not os.path.isfile(_STATE_FILE_PATH):
        interfaces.StateInterface.initialize()

    with open(_STATE_FILE_PATH, "r") as f:
        try:
            state_content = json.load(f)
        except:
            raise AssertionError("file not in a valid json format")

    click.echo(json.dumps(state_content, indent=(2 if indent else None)))


@click.group()
def state_command_group() -> None:
    pass


state_command_group.add_command(_get_state, name="get")
