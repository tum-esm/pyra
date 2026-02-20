"""Pyra CLI entry point. Use `pyra-cli --help`/`pyra-cli $command --help`
to see all available commands.`"""

import sys

import click
import tum_esm_utils

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
sys.path.append(_PROJECT_DIR)

from packages.cli.commands import (
    config_command_group,
    core_command_group,
    logs_command_group,
    remove_filelocks,
    state_command_group,
    test_command_group,
    tum_enclosure_command_group,
    aemet_enclosure_command_group,
)
from packages.core import utils

logger = utils.Logger(origin="cli", lock=None)


@click.command(help="Print Pyra version and code directory path.")
def print_cli_information() -> None:
    logger.debug('running command "info"')
    click.echo(
        click.style(
            f'This CLI is running Pyra version 5.0.0-beta.2 in directory "{_PROJECT_DIR}"',
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
cli.add_command(tum_enclosure_command_group, name="tum-enclosure")
cli.add_command(aemet_enclosure_command_group, name="aemet-enclosure")
cli.add_command(remove_filelocks, name="remove-filelocks")
cli.add_command(state_command_group, name="state")
cli.add_command(test_command_group, name="test")

if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
