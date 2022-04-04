import click
import os
import sys

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)

from packages.cli.commands import config as config_commands
from packages.cli.commands.logs import logs_command_group


@click.group()
def cli():
    pass


cli.add_command(config_commands.get_setup)
cli.add_command(config_commands.get_parameters)
cli.add_command(config_commands.set_setup)
cli.add_command(config_commands.set_parameters)
cli.add_command(config_commands.validate_current_setup)
cli.add_command(config_commands.validate_current_parameters)

cli.add_command(logs_command_group, name="logs")


if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
