import json
import click
import os
import sys
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", "config.lock")


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
        with filelock.FileLock(CONFIG_LOCK_PATH):
            return function(*args, **kwargs)

    return locked_function


def update_dict_rec(old_dict, new_dict):
    if old_dict is None or new_dict is None:
        return new_dict
    if type(old_dict) not in [int, float] and type(new_dict) not in [int, float]:
        assert type(old_dict) == type(
            new_dict
        ), f"{old_dict} = {type(old_dict)} -> {new_dict} = {type(new_dict)}"
    if type(old_dict) == dict:
        updated_dict = {}
        for key in old_dict.keys():
            if key in new_dict:
                updated_dict[key] = update_dict_rec(old_dict[key], new_dict[key])
            else:
                updated_dict[key] = old_dict[key]
        return updated_dict
    else:
        return new_dict


@click.command(help="Read the current config.json file.")
@with_filelock
def _get_config():
    try:
        assert os.path.isfile(CONFIG_FILE_PATH), "file does not exist"
        with open(CONFIG_FILE_PATH, "r") as f:
            try:
                content = json.load(f)
            except:
                raise AssertionError("file not in a valid json format")
        click.echo(json.dumps(content))
    except AssertionError as e:
        error_handler(e)


@click.command(
    short_help="Set the config.json file.",
    help=f"Set config. Pass the JSON directly or via a file path. Only a subset of the required config variables has to be passed. The non-occuring values will be reused from the current config.\n\nThe required schema can be found in the documentation.",
)
@click.argument("content", default="{}")
@with_filelock
def _update_config(content: str):
    # The validation itself might print stuff using the error_handler
    if not Validation.check_partial_config_string(content):
        return
    new_partial_json = json.loads(content)

    with open(CONFIG_FILE_PATH, "r") as f:
        current_json: dict = json.load(f)

    merged_json = update_dict_rec(current_json, new_partial_json)
    with open(CONFIG_FILE_PATH, "w") as f:
        json.dump(merged_json, f)

    success_handler("Updated config file")


@click.command(
    help=f"Validate the current config.json file.\n\nThe required schema can be found in the documentation."
)
@with_filelock
def _validate_current_config():
    # The validation itself might print stuff using the error_handler
    if Validation.check_current_config_file():
        success_handler(f"Current config file is valid")


@click.group()
def config_command_group():
    pass


config_command_group.add_command(_get_config, name="get")
config_command_group.add_command(_update_config, name="update")
config_command_group.add_command(_validate_current_config, name="validate")
