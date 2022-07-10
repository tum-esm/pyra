import json
import shutil
import click
import os
import sys
from packages.core.utils import with_filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
DEFAULT_CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.default.json")
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")


sys.path.append(PROJECT_DIR)
from packages.core.utils import ConfigValidation

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))
ConfigValidation.logging_handler = error_handler


def update_dict_rec(old_object, new_object):
    if old_object is None or new_object is None:
        return new_object

    if type(old_object) == dict:
        assert type(new_object) == dict
        updated_dict = {}
        for key in old_object.keys():
            if key in new_object:
                updated_dict[key] = update_dict_rec(old_object[key], new_object[key])
            else:
                updated_dict[key] = old_object[key]
        return updated_dict
    else:
        if type(old_object) in [int, float]:
            assert type(new_object) in [int, float]
        else:
            assert type(old_object) == type(new_object)
        return new_object


@click.command(help="Read the current config.json file.")
@with_filelock(CONFIG_LOCK_PATH)
def _get_config():
    if not os.path.isfile(CONFIG_FILE_PATH):
        shutil.copyfile(DEFAULT_CONFIG_FILE_PATH, CONFIG_FILE_PATH)
    with open(CONFIG_FILE_PATH, "r") as f:
        try:
            content = json.load(f)
        except:
            raise AssertionError("file not in a valid json format")
    click.echo(json.dumps(content))


@click.command(
    short_help="Set the config.json file.",
    help=f"Set config. Pass the JSON directly or via a file path. Only a subset of the required config variables has to be passed. The non-occuring values will be reused from the current config.\n\nThe required schema can be found in the documentation.",
)
@click.argument("content", default="{}")
@with_filelock(CONFIG_LOCK_PATH)
def _update_config(content: str):
    # The validation itself might print stuff using the error_handler
    if not ConfigValidation.check_partial_config_string(content):
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
@with_filelock(CONFIG_LOCK_PATH)
def _validate_current_config():
    # The validation itself might print stuff using the error_handler
    file_is_valid, _ = ConfigValidation.check_current_config_file()
    if file_is_valid:
        success_handler(f"Current config file is valid")


@click.group()
def config_command_group():
    pass


config_command_group.add_command(_get_config, name="get")
config_command_group.add_command(_update_config, name="update")
config_command_group.add_command(_validate_current_config, name="validate")
