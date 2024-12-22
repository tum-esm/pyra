"""Read the current state.json file."""

import click

from packages.core import interfaces, utils

logger = utils.Logger(origin="cli")


@click.group()
def state_command_group() -> None:
    pass


@state_command_group.command(name="get", help="Read the current state.json file.")
@click.option("--indent", is_flag=True, help="Print the JSON in an indented manner")
def _get_state(indent: bool) -> None:
    logger.debug('running command "state get"')
    state = interfaces.StateInterface.load_state()
    click.echo(state.model_dump_json(indent=(2 if indent else None)))
