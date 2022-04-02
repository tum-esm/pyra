import click
import os
import sys

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)

from packages.cli.commands.config import cli_commands


@click.group()
def cli():
    pass


for filetype in ["setup", "parameters"]:
    cli.add_command(cli_commands[filetype]["get"], f"get-{filetype}")
    cli.add_command(cli_commands[filetype]["set"], f"set-{filetype}")
    cli.add_command(cli_commands[filetype]["validate"], f"validate-current-{filetype}")


if __name__ == "__main__":
    print(cli_commands["setup"]["get"])
    cli.main(prog_name="pyra-cli")
