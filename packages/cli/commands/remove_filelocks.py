"""Not doing anything because Pyra >= 4.2.4 is no longer using file locks."""

import click


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


# FIXME: remove with next breaking release
@click.command(
    name="remove-filelocks",
    help="Not doing anything because Pyra >= 4.2.4 is no longer using file locks.",
)
def remove_filelocks() -> None:
    _print_green("Not doing anything because Pyra >= 4.2.4 is no longer using file locks.")
