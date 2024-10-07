"""Read current `debug.log` log file."""

# FIXME: remove this entirely with the next breaking release

import click
import os

import tum_esm_utils
from packages.core import interfaces, utils

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_DEBUG_LOG_FILE = os.path.join(_PROJECT_DIR, "logs", "debug.log")
_LOG_FILES_LOCK = os.path.join(_PROJECT_DIR, "logs", ".logs.lock")

logger = utils.Logger(origin="cli")


@click.group()
def logs_command_group() -> None:
    pass


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@logs_command_group.command(
    name="read",
    help="Read the current info.log or debug.log file.",
)
@click.option("--level", default="DEBUG", help="Log level INFO or DEBUG")
@tum_esm_utils.decorators.with_filelock(
    lockfile_path=_LOG_FILES_LOCK,
    timeout=5,
)
def _read_logs(level: str) -> None:
    logger.info('running command "logs read"')

    if level == "INFO":
        _print_red("Pyra ^4.1 does not have info log files anymore, only debug log files.")
    if level not in ["INFO", "DEBUG"]:
        _print_red("Level has to be either INFO or DEBUG.")
        exit(1)

    with open(_DEBUG_LOG_FILE, "r") as f:
        click.echo("".join(f.readlines()))


@logs_command_group.command(
    name="archive",
    help=
    "Archive the current log files. This command will write all log lines from the current info.log and debug.log files into the logs/archive directory."
)
def _archive_logs() -> None:
    interfaces.StateInterface.update_state(recent_cli_calls=1)
    logger.info('running command "logs archive"')

    utils.Logger.archive()
    _print_red("this command is deprecated without a replacement")
