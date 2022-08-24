import click
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


def print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.command(
    help="Remove all filelocks. Helpful when any of the programs crashed "
    + "during writing to a file. Should not be necessary normally."
)
def remove_filelocks() -> None:
    lock_files = [
        os.path.join(PROJECT_DIR, "config", ".config.lock"),
        os.path.join(PROJECT_DIR, "config", ".state.lock"),
        os.path.join(PROJECT_DIR, "logs", ".logs.lock"),
    ]
    for f in lock_files:
        if os.path.isfile(f):
            os.remove(f)
            print_green(f"Removing {f}")
    print_green("Done!")
