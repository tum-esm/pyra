import json
import logging
import click
import os
import sys
from filelock import FileLock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"

sys.path.append(PROJECT_DIR)
from packages.core.validation import Validation, PARAMS_FILE_SCHEMA

error_handler = lambda m: click.echo(click.style(m, fg="red"))
success_handler = lambda m: click.echo(click.style(m, fg="green"))

cli_commands = {
    "setup": {},
    "parameters": {},
}

for filetype in ["setup", "parameters"]:

    JSON_FILE_PATH = f"{PROJECT_DIR}/config/{filetype}.json"

    def check_file(
        file_path=JSON_FILE_PATH,
        content_string=None,
        partial_validation=True,
    ):
        (
            Validation.check_parameters_file
            if filetype == "parameters"
            else Validation.check_setup_file
        )(
            file_path=file_path,
            content_string=content_string,
            logging_handler=error_handler,
            logging_message=f"Error in current {filetype} file: ",
            partial_validation=partial_validation,
        )

    @click.command(help=f"Read the current {filetype}.json file.")
    def get():
        try:
            with FileLock(CONFIG_LOCK_PATH):
                assert os.path.isfile(JSON_FILE_PATH), "file does not exist"
                with open(JSON_FILE_PATH, "r") as f:
                    try:
                        content = json.load(f)
                    except:
                        raise AssertionError("file not in a valid json format")
                success_handler(content)
        except AssertionError as e:
            error_handler(e)

    @click.command(
        help=f"Set {filetype}. Pass the JSON directly or via a file path. Only a subset of the required {filetype} variables has to be passed. The non-occuring values will be reused from the current config."
    )
    @click.option("--path", default="", help="Path to JSON file")
    @click.option("--content", default="", help="Content of JSON file")
    def _set(path: str, content: str):
        if (path == "" and content == "") or (path != "" and content != ""):
            click.echo('You have to pass exactly one of "--path" or "--content"')
        else:
            if path != "":
                if not check_file(file_path=path):
                    return
                with open(path, "r") as f:
                    new_partial_json: dict = json.load(f)
            else:
                if not check_file(content_string=content):
                    return
                new_partial_json = json.loads(content)

            with FileLock(CONFIG_LOCK_PATH):
                if not check_file():
                    return
                with open(JSON_FILE_PATH, "r") as f:
                    current_json: dict = json.load(f)

                with open(JSON_FILE_PATH, "w") as f:
                    json.dump({**current_json, **new_partial_json}, f)

            success_handler(f"Updated {filetype} file")

    @click.command(help=f"Validate the current {filetype}.json file.")
    def _validate():
        if check_file():
            success_handler(
                f"Current {filetype} file is invalid, required schema: {PARAMS_FILE_SCHEMA}"
            )

    cli_commands[filetype]["get"] = get
    cli_commands[filetype]["set"] = _set
    cli_commands[filetype]["validate"] = _validate
