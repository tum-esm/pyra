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
@with_filelock
def _get_state():
    try:
        assert os.path.isfile(STATE_FILE_PATH), "pyra-core is not running"
        with open(STATE_FILE_PATH, "r") as f:
            try:
                content = json.load(f)
            except:
                raise AssertionError("file not in a valid json format")
        click.echo(json.dumps(content))

        # TODO: Add option to display state in a pretty way
    except AssertionError as e:
        error_handler(e)


@click.group()
def state_command_group():
    pass


state_command_group.add_command(_get_state, name="get")
