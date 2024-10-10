"""Interact with log files"""

from typing import Optional
import click
import os
import re
import glob
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


# FIXME: remove this with the next breaking release
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


# FIXME: remove this with the next breaking release
@logs_command_group.command(
    name="archive",
    help=
    "Archive the current log files. This command will write all log lines from the current info.log and debug.log files into the logs/archive directory."
)
def _archive_logs() -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info('running command "logs archive"')

    utils.Logger.archive()
    _print_red("this command is deprecated without a replacement")


@logs_command_group.command(name="split-log-files-by-origin")
@click.argument(
    "path",
    type=str,
    default="./*.log",
    help="Path to the log files. You can use UNIX-style wildcards."
)
def split_log_files_by_origin(path: str) -> None:
    """Split log files by origin."""

    logger.info(f'running command "logs split-log-files-by-origin {path}"')
    line_with_origin_pattern = re.compile(
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+ [^\s]+ \- ([\w\d\-_]+) \- '
    )
    # 2024-10-09 01:40:16.089891 UTC+0 - enclosure-control -

    filepaths = glob.glob(path)

    for f in filepaths:
        if not os.path.isfile(f):
            print(f"Not a file: {f}")
            continue
        if not f.endswith(".log"):
            print(f"Not a log file: {f} (has to end with `.log`)")
            continue

        print(f"Splitting {f}")
        with open(f, 'r') as file:
            lines = file.read().strip(" \t\n").split("\n")

        data: dict[str, list[str]] = {}
        origin: Optional[str] = None
        for line in lines:
            if line_with_origin_pattern.match(line):
                origin = line_with_origin_pattern.match(line).group(1)
                if origin not in data:
                    data[origin] = []

            if origin is not None:
                data[origin].append(line)

        if len(data) == 0:
            print(f"No origin found in {f}")
            continue
        if len(data) == 1:
            print(f"Only one origin found in {f} (not splitting)")
            continue

        for origin, lines in data.items():
            new_path = f"{f[:-4]}-{origin}.log"
            print(f"Writing logs subset to {new_path}")
            with open(new_path, 'w') as file:
                file.write("\n".join(lines))
