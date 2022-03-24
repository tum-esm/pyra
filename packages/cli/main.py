import json
import click
import os
import sys
from filelock import FileLock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"

sys.path.append(PROJECT_DIR)
from packages.core.validation import Validation


error_handler = lambda m: click.echo(click.style(m, fg="red"))
success_handler = lambda m: click.echo(click.style(m, fg="green"))
VALIDATION_KWARGS = lambda label: {
    "logging_handler": error_handler,
    "logging_message": f"New {label} invalid: ",
    "partial_validation": True,
}


@click.group()
def cli():
    pass


@click.command(
    help="Set parameters. Pass the JSON directly or via a file path. Only a subset of the required parameters has to be passed. The non-occuring values will be reused from the current config."
)
@click.option("--path", default="", help="Path to JSON file")
@click.option("--content", default="", help="Content of JSON file")
def set_parameters(path: str, content: str):
    if (path == "" and content == "") or (path != "" and content != ""):
        click.echo('You have to pass exactly one of "--path" or "--content"')
    else:
        if path != "":
            if not Validation.check_parameters_file(
                file_path=path, **VALIDATION_KWARGS("parameters")
            ):
                return
            with open(path, "r") as f:
                new_partial_params: dict = json.load(f)
        else:
            if not Validation.check_parameters_file(
                content_string=content, **VALIDATION_KWARGS("parameters")
            ):
                return
            new_partial_params = json.loads(content)

        with FileLock(CONFIG_LOCK_PATH):
            if not Validation.check_parameters_file(logging_handler=error_handler):
                return
            with open(PARAMS_FILE_PATH, "r") as f:
                current_params: dict = json.load(f)

            with open(PARAMS_FILE_PATH, "w") as f:
                json.dump({**current_params, **new_partial_params}, f)

        success_handler("Updated parameters file")


@click.command(help="Read the current parameters.json file.")
def get_parameters():
    try:
        assert os.path.isfile(PARAMS_FILE_PATH), "file does not exist"
        with open(PARAMS_FILE_PATH, "r") as f:
            try:
                content = json.load(f)
            except:
                raise AssertionError("file not in a valid json format")
        success_handler(content)
    except AssertionError as e:
        error_handler(e)


@click.command(help="Validate the current parameters.json file.")
def validate_current_parameters():
    if Validation.check_parameters_file(logging_handler=error_handler):
        success_handler("Current parameters file is valid")


cli.add_command(set_parameters)
cli.add_command(get_parameters)
cli.add_command(validate_current_parameters)

if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
