import click
import os
import sys
from packages.cli.commands.config import (
    set_parameters,
    get_parameters,
    validate_current_parameters,
)

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)


@click.group()
def cli():
    pass


cli.add_command(set_parameters)
cli.add_command(get_parameters)
cli.add_command(validate_current_parameters)

# TODO: commands for setup

if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
