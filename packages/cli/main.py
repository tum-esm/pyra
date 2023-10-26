"""Pyra CLI entry point. Use `pyra-cli --help`/`pyra-cli $command --help`
to see all available commands.`"""

import click
import os
import sys

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(os.path.abspath(__file__))))
sys.path.append(_PROJECT_DIR)

from packages.core import types
from packages.cli.commands import (
    config_command_group,
    core_command_group,
    logs_command_group,
    plc_command_group,
    remove_filelocks,
    state_command_group,
    test_command_group,
)


@click.command(help="Print Pyra version and code directory path.")
def print_cli_information() -> None:
    config = types.Config.load()
    click.echo(
        click.style(
            f'This CLI is running Pyra version {config.general.version}' +
            f' in directory "{_PROJECT_DIR}".',
            fg="green",
        )
    )


@click.group()
def cli() -> None:
    pass


cli.add_command(print_cli_information, name="info")
cli.add_command(config_command_group, name="config")
cli.add_command(core_command_group, name="core")
cli.add_command(logs_command_group, name="logs")
cli.add_command(plc_command_group, name="plc")
cli.add_command(remove_filelocks, name="remove-filelocks")
cli.add_command(state_command_group, name="state")
cli.add_command(test_command_group, name="test")

if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
