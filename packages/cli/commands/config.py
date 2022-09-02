import json
import shutil
import click
import os
import sys
from packages.core import types
from packages.core.utils import with_filelock, update_dict_recursively

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
DEFAULT_CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.default.json")
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")


sys.path.append(PROJECT_DIR)


def print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.command(help="Read the current config.json file.")
@with_filelock(CONFIG_LOCK_PATH)
def _get_config() -> None:
    if not os.path.isfile(CONFIG_FILE_PATH):
        shutil.copyfile(DEFAULT_CONFIG_FILE_PATH, CONFIG_FILE_PATH)
    with open(CONFIG_FILE_PATH, "r") as f:
        try:
            content = json.load(f)
        except:
            raise AssertionError("file not in a valid json format")

    types.validate_config_dict(content, partial=False, skip_filepaths=True)
    click.echo(json.dumps(content))


@click.command(
    short_help="Set the config.json file.",
    help=f"Set config. Pass the JSON directly or via a file path. Only a subset of the required config variables has to be passed. The non-occuring values will be reused from the current config.\n\nThe required schema can be found in the documentation.",
)
@click.argument("content", default="{}")
@with_filelock(CONFIG_LOCK_PATH)
def _update_config(content: str) -> None:
    # try to load the dict
    try:
        new_partial_json = json.loads(content)
    except:
        print_red("content argument is not a valid JSON string")
        return

    # validate the dict's integrity
    try:
        types.validate_config_dict(new_partial_json, partial=True)
    except Exception as e:
        print_red(str(e))
        return

    # load the current json file
    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            current_json = json.load(f)
    except:
        print_red("Could not load the current config.json file")
        return

    # merge current config and new partial config
    merged_json = update_dict_recursively(current_json, new_partial_json)
    with open(CONFIG_FILE_PATH, "w") as f:
        json.dump(merged_json, f, indent=4)

    print_green("Updated config file")


@click.command(
    help=f"Validate the current config.json file.\n\nThe required schema can be found in the documentation."
)
@with_filelock(CONFIG_LOCK_PATH)
def _validate_current_config() -> None:
    # load the current json file
    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            current_json = json.load(f)
    except:
        print_red("Could not load the current config.json file")
        return

    # validate its integrity
    try:
        types.validate_config_dict(current_json, partial=False)
    except Exception as e:
        print_red(str(e))
        return

    print_green(f"Current config file is valid")


@click.group()
def config_command_group() -> None:
    pass


config_command_group.add_command(_get_config, name="get")
config_command_group.add_command(_update_config, name="update")
config_command_group.add_command(_validate_current_config, name="validate")
