from datetime import datetime
import click
import os
from packages.core.utils import with_filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INFO_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "info.log")
DEBUG_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "debug.log")
LOG_FILES_LOCK = os.path.join(PROJECT_DIR, "logs", ".logs.lock")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


def is_valid_log_line(log_line: str):
    try:
        assert len(log_line) >= 10
        datetime.strptime(log_line[:10], "%Y-%m-%d")
        return True
    except:
        return False


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
@with_filelock(LOG_FILES_LOCK)
def _archive_logs():
    for filetype in ["info", "debug"]:
        _filepath = INFO_LOG_FILE if filetype == "info" else DEBUG_LOG_FILE
        with open(_filepath, "r") as f:
            new_log_lines = f.readlines()
        with open(_filepath, "w") as f:
            pass
        new_log_date_groups = {}
        for line in new_log_lines:
            if is_valid_log_line(line):
                date = line[:10]
                if date not in new_log_date_groups.keys():
                    new_log_date_groups[date] = []
                new_log_date_groups[date].append(line)

        for date_group, lines in new_log_date_groups.items():
            with open(
                os.path.join(
                    PROJECT_DIR,
                    "logs",
                    "archive",
                    f"{date_group.replace('-', '')}-{filetype}.log",
                ),
                "a",
            ) as f:
                f.writelines(lines)
                f.write("\n")
    success_handler("done!")


@click.group()
def logs_command_group():
    pass


logs_command_group.add_command(_read_logs, name="read")
logs_command_group.add_command(_archive_logs, name="archive")
