import click
import os
import sys

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)

from packages.cli.commands.config import config_command_group
from packages.cli.commands.state import state_command_group
from packages.cli.commands.logs import logs_command_group
from packages.cli.commands.core import core_command_group
from packages.cli.commands.remove_filelocks import remove_filelocks


@click.group()
def cli():
    pass


cli.add_command(config_command_group, name="config")
cli.add_command(state_command_group, name="state")
cli.add_command(logs_command_group, name="logs")
cli.add_command(core_command_group, name="core")
cli.add_command(remove_filelocks, name="remove-filelocks")


if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
