"""Remove file locks that might be corrupted."""

import os
import click
from packages.core import interfaces


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


@click.command(
    name="remove-filelocks",
    help="NRemove file locks that might be corrupted.",
)
def remove_filelocks() -> None:
    for f in [
        interfaces.state_interface.STATE_LOCK_PATH,
        interfaces.state_interface.STATE_LOCK_PATH + "-journal",
    ]:
        if os.path.exists(f):
            os.remove(f)
            _print_green(f"Removed {f} lock.")
