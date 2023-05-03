"""Read current `info.log`/`debug.log` files."""

import click
import os

import tum_esm_utils
from packages.core.utils import Logger

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_INFO_LOG_FILE = os.path.join(_PROJECT_DIR, "logs", "info.log")
_DEBUG_LOG_FILE = os.path.join(_PROJECT_DIR, "logs", "debug.log")
_LOG_FILES_LOCK = os.path.join(_PROJECT_DIR, "logs", ".logs.lock")


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.command(help="Read the current info.log or debug.log file.")
@click.option("--level", default="INFO", help="Log level INFO or DEBUG")
@tum_esm_utils.decorators.with_filelock(
    lockfile_path=_LOG_FILES_LOCK,
    timeout=5,
)
def _read_logs(level: str) -> None:
    if level in ["INFO", "DEBUG"]:
        with open(_INFO_LOG_FILE if level == "INFO" else _DEBUG_LOG_FILE, "r") as f:
            click.echo("".join(f.readlines()))
    else:
        _print_red("Level has to be either INFO or DEBUG.")


@click.command(
    help="Archive the current log files. This command will write all log lines from the current info.log and debug.log files into the logs/archive directory."
)
def _archive_logs() -> None:
    Logger.archive()
    _print_green("done!")


@click.group()
def logs_command_group() -> None:
    pass


logs_command_group.add_command(_read_logs, name="read")
logs_command_group.add_command(_archive_logs, name="archive")
