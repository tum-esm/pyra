"""Remove all filelocks. Helpful when any of the programs crashed during
writing to a file. Normally, this should not be necessary."""

import os

import click

from packages.core import interfaces, utils

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
logger = utils.Logger(origin="cli", lock=None)


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


@click.command(
    name="remove-filelocks",
    help="Remove all filelocks. Helpful when any of the programs crashed during writing to a file. Normally, this should not be necessary.",
)
def remove_filelocks() -> None:
    with interfaces.StateInterface.update_state(logger) as s:
        s.activity.cli_calls += 1
    logger.debug('running command "remove-filelocks"')
    lock_files = [
        os.path.join(_PROJECT_DIR, "config", ".config.lock"),
        os.path.join(_PROJECT_DIR, "config", ".state.lock"),
        os.path.join(_PROJECT_DIR, "logs", ".logs.lock"),
    ]
    for f in lock_files:
        if os.path.isfile(f):
            os.remove(f)
            _print_green(f"Removing {f}")
    _print_green("Done!")
