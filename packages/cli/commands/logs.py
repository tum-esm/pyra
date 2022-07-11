import click
import os
from packages.core.utils import with_filelock, Logger

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INFO_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "info.log")
DEBUG_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "debug.log")
LOG_FILES_LOCK = os.path.join(PROJECT_DIR, "logs", ".logs.lock")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


@click.command(help="Read the current info.log or debug.log file.")
@click.option("--level", default="INFO", help="Log level INFO or DEBUG")
@with_filelock(LOG_FILES_LOCK)
def _read_logs(level: str):
    if level in ["INFO", "DEBUG"]:
        with open(INFO_LOG_FILE if level == "INFO" else DEBUG_LOG_FILE, "r") as f:
            click.echo("".join(f.readlines()))
    else:
        error_handler("Level has to be either INFO or DEBUG.")


@click.command(help="Archive the current log files.")
def _archive_logs():
    Logger.archive()
    success_handler("done!")


@click.group()
def logs_command_group():
    pass


logs_command_group.add_command(_read_logs, name="read")
logs_command_group.add_command(_archive_logs, name="archive")
