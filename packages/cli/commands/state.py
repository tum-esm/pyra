"""Read and update the current state.json file."""

# pyright: reportUnusedFunction=false

import click
import tum_esm_utils

from packages.core import utils, interfaces

logger = utils.Logger(origin="cli", lock=None)


@click.group()
def state_command_group() -> None:
    pass


@state_command_group.command(name="get", help="Read the current state.json file.")
@click.option("--indent", is_flag=True, help="Print the JSON in an indented manner")
def _get_state(indent: bool) -> None:
    logger.debug('running command "state get"')
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )
    state = interfaces.StateInterface.load_state(state_lock, logger)
    click.echo(state.model_dump_json(indent=(2 if indent else None)))


@state_command_group.command(
    name="resolve-exceptions", help="Mark all active exceptions as resolved."
)
def _resolve_exceptions() -> None:
    logger.debug('running command "state resolve-exceptions"')
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )
    interfaces.ExceptionsInterface(state_lock, logger).resolve_all_exceptions()
    click.echo("All active exceptions marked as resolved.")
