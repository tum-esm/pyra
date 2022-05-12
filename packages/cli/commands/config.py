import json
import click
import os
import sys
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = os.path.join(PROJECT_DIR, "config", "setup.json")
PARAMS_FILE_PATH = os.path.join(PROJECT_DIR, "config", "parameters.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", "config.lock")


sys.path.append(PROJECT_DIR)
from packages.core.utils.validation import Validation

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


@click.command(help="Read the current setup.json file.")
@with_filelock
def _get_setup():
    try:
        assert os.path.isfile(SETUP_FILE_PATH), "file does not exist"
        with open(SETUP_FILE_PATH, "r") as f:
            try:
                content = json.load(f)
            except:
                raise AssertionError("file not in a valid json format")
        click.echo(json.dumps(content))
    except AssertionError as e:
        error_handler(e)


@click.command(help="Read the current parameters.json file.")
@with_filelock
def _get_parameters():
    try:
        assert os.path.isfile(PARAMS_FILE_PATH), "file does not exist"

        with open(PARAMS_FILE_PATH, "r") as f:
            try:
                content = json.load(f)
            except:
                raise AssertionError("file not in a valid json format")
        click.echo(json.dumps(content))
    except AssertionError as e:
        error_handler(e)


@click.command(
    short_help="Set the setup.json file.",
    help=f"Set setup. Pass the JSON directly or via a file path. Only a subset of the required setup variables has to be passed. The non-occuring values will be reused from the current config.\n\nThe required schema can be found in the documentation.",
)
@click.option("--path", default="", help="Path to JSON file")
@click.option("--content", default="", help="Content of JSON file")
@with_filelock
def _update_setup(path: str, content: str):
    if (path == "" and content == "") or (path != "" and content != ""):
        click.echo('You have to pass exactly one of "--path" or "--content"')
    else:
        if path != "":
            if not Validation.check_setup_file(
                file_path=path,
                logging_message=f"New setup invalid: ",
                partial_validation=True,
            ):
                return
            with open(path, "r") as f:
                new_partial_json: dict = json.load(f)
        else:
            if not Validation.check_setup_file(
                content_string=content,
                logging_message=f"New setup invalid: ",
                partial_validation=True,
            ):
                return
            new_partial_json = json.loads(content)

        with open(SETUP_FILE_PATH, "r") as f:
            current_json: dict = json.load(f)

        merged_json = update_dict_rec(current_json, new_partial_json)
        with open(SETUP_FILE_PATH, "w") as f:
            json.dump(merged_json, f)

        success_handler("Updated setup file")


@click.command(
    short_help="Set the parameters.json file.",
    help=f"Set parameters. Pass the JSON directly or via a file path. Only a subset of the required parameters has to be passed. The non-occuring values will be reused from the current config.\n\nThe required schema can be found in the documentation.",
)
@click.option("--path", default="", help="Path to JSON file")
@click.option("--content", default="", help="Content of JSON file")
@with_filelock
def _update_parameters(path: str, content: str):
    if (path == "" and content == "") or (path != "" and content != ""):
        click.echo('You have to pass exactly one of "--path" or "--content"')
    else:
        if path != "":
            if not Validation.check_parameters_file(
                file_path=path,
                logging_message=f"New parameters invalid: ",
                partial_validation=True,
            ):
                return
            with open(path, "r") as f:
                new_partial_json: dict = json.load(f)
        else:
            if not Validation.check_parameters_file(
                content_string=content,
                logging_message=f"New parameters invalid: ",
                partial_validation=True,
            ):
                return
            new_partial_json = json.loads(content)

        with open(PARAMS_FILE_PATH, "r") as f:
            current_json: dict = json.load(f)

        merged_json = update_dict_rec(current_json, new_partial_json)
        with open(PARAMS_FILE_PATH, "w") as f:
            json.dump(merged_json, f)

        success_handler("Updated parameters file")


@click.command(
    help=f"Validate the current setup.json file.\n\nThe required schema can be found in the documentation."
)
@with_filelock
def _validate_setup():
    if Validation.check_setup_file():
        success_handler(f"Current setup file is valid")


@click.command(
    help=f"Validate the current parameters.json file.\n\nThe required schema can be found in the documentation."
)
@with_filelock
def _validate_parameters():
    if Validation.check_parameters_file():
        success_handler(f"Current parameters file is valid")


@click.group()
def _setup_config_command_group():
    pass


_setup_config_command_group.add_command(_get_setup, name="get")
_setup_config_command_group.add_command(_update_setup, name="update")
_setup_config_command_group.add_command(_validate_setup, name="validate")


@click.group()
def _parameters_config_command_group():
    pass


_parameters_config_command_group.add_command(_get_parameters, name="get")
_parameters_config_command_group.add_command(_update_parameters, name="update")
_parameters_config_command_group.add_command(_validate_parameters, name="validate")


@click.group()
def config_command_group():
    pass


config_command_group.add_command(_setup_config_command_group, name="setup")
config_command_group.add_command(_parameters_config_command_group, name="parameters")
