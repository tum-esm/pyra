"""Read or update the `config.json` file."""

import json
import shutil
import click
import os

import tum_esm_utils
from packages.core import types

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_DEFAULT_CONFIG_FILE_PATH = os.path.join(
    _PROJECT_DIR, "config", "config.default.json"
)
_CONFIG_FILE_PATH = os.path.join(_PROJECT_DIR, "config", "config.json")
_CONFIG_LOCK_PATH = os.path.join(_PROJECT_DIR, "config", ".config.lock")


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.option("--no-indent", default=False, is_flag=True)
@click.option("--check-path-existence", default=False, is_flag=True)
@click.option("--no-color", default=False, is_flag=True)
@click.command(
    short_help="Read the config.json file.",
    help=
    "Read the current config.json file. If it does not exist, use the config.default.json as the config.json. The command validates the structure of the config.json but skips verifying filepath existence.",
)
def _get_config(
    no_indent: bool, check_path_existence: bool, no_color: bool
) -> None:
    if not os.path.isfile(_CONFIG_FILE_PATH):
        shutil.copyfile(_DEFAULT_CONFIG_FILE_PATH, _CONFIG_FILE_PATH)
    try:
        config = types.Config.load(
            ignore_path_existence=(not check_path_existence)
        )
    except ValueError as e:
        click.echo(click.style(e, fg=None if no_color else "red"))
        exit(1)

    click.echo(
        click.style(
            config.model_dump_json(indent=None if no_indent else 4),
            fg=None if no_color else "green"
        )
    )


@click.command(
    short_help="Update the config.json file.",
    help=
    f"Update config. Only a subset of the required config variables has to be passed. The non-occuring values will be reused from the current config.\n\nThe required schema can be found in the documentation (user guide -> usage).",
)
@click.argument("content", default="{}")
@tum_esm_utils.decorators.with_filelock(
    lockfile_path=_CONFIG_LOCK_PATH,
    timeout=5,
)
def _update_config(content: str) -> None:
    try:
        current_config = types.Config.load(
            with_filelock=False,
            ignore_path_existence=True,
        )
    except Exception as e:
        raise RuntimeError(f"Could not load the current config.json file: {e}")

    try:
        new_partial_config = types.PartialConfig.load(
            content,
            ignore_path_existence=True,
        )
    except ValueError as e:
        error_message = str(e)
        _print_red(
            error_message.replace(
                "ConfigPartial is invalid", "Config update is invalid"
            )
        )
        exit(1)

    merged_config_dicts = tum_esm_utils.datastructures.merge_dicts(
        current_config.model_dump(),
        new_partial_config.model_dump(exclude_unset=True),
    )
    merged_config = types.Config.load(
        merged_config_dicts,
        ignore_path_existence=True,
    )

    with open(_CONFIG_FILE_PATH, "w") as f:
        f.write(merged_config.model_dump_json(indent=4))

    _print_green("Updated config file")


@click.command(
    help=
    f"Validate the current config.json file.\n\nThe required schema can be found in the documentation (user guide -> usage). This validation will check filepath existence."
)
def _validate_current_config() -> None:
    try:
        types.Config.load()
    except Exception as e:
        _print_red(f"Current config file is invalid\n{e}")
        exit(1)

    _print_green(f"Current config file is valid")


@click.group()
def config_command_group() -> None:
    pass


config_command_group.add_command(_get_config, name="get")
config_command_group.add_command(_update_config, name="update")
config_command_group.add_command(_validate_current_config, name="validate")
