import click
import os
import sys

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)

from .commands import (
    config_command_group,
    core_command_group,
    logs_command_group,
    plc_command_group,
    remove_filelocks,
    state_command_group,
)


@click.group()
def cli() -> None:
    pass


cli.add_command(config_command_group, name="config")
cli.add_command(core_command_group, name="core")
cli.add_command(logs_command_group, name="logs")
cli.add_command(plc_command_group, name="plc")
cli.add_command(remove_filelocks, name="remove-filelocks")
cli.add_command(state_command_group, name="state")


if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
