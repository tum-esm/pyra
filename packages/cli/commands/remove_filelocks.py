import click
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


@click.command(
    help="Remove all filelocks. Helpful when any of the programs crashed "
    + "during writing to a file. Should not be necessary normally."
)
def remove_filelocks():
    lock_files = [
        os.path.join(PROJECT_DIR, "config", ".config.lock"),
        os.path.join(PROJECT_DIR, "logs", ".logs.lock"),
        os.path.join(PROJECT_DIR, "state", ".state.lock"),
    ]
    if input("Are you sure? (y) ").startswith("y"):
        for f in lock_files:
            if os.path.isfile(f):
                os.remove(f)
                success_handler(f"Removing {f}")
        success_handler("Done!")
    else:
        error_handler("Aborting")
