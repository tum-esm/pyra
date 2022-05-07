import click
import os
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INFO_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "info.log")
DEBUG_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "debug.log")
LOG_FILES_LOCK = os.path.join(PROJECT_DIR, "logs", "logs.lock")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))

# FileLock = Mark, that the config JSONs are being used and the
# CLI should not interfere. A file "config/config.lock" will be created
# and the existence of this file will make the next line wait.
def with_filelock(function):
    def locked_function(*args, **kwargs):
        with filelock.FileLock(LOG_FILES_LOCK):
            return function(*args, **kwargs)

    return locked_function


@click.command(help="Read the current info.log or debug.log file.")
@click.option("--level", default="INFO", help="Log level INFO or DEBUG")
@with_filelock
def _read_logs(level: str):
    if level in ["INFO", "DEBUG"]:
        with open(INFO_LOG_FILE if level == "INFO" else DEBUG_LOG_FILE, "r") as f:
            click.echo("".join(f.readlines()))
    else:
        error_handler("Level has to be either INFO or DEBUG.")


@click.command(help="Archive the current log files.")
@with_filelock
def _archive_logs():
    for filetype in ["info", "debug"]:
        _filepath = INFO_LOG_FILE if filetype == "info" else DEBUG_LOG_FILE
        with open(_filepath, "r") as f:
            new_log_lines = f.readlines()
        with open(_filepath, "w") as f:
            pass
        new_log_date_groups = {}
        for line in new_log_lines:
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


@click.group()
def logs_command_group():
    pass


logs_command_group.add_command(_read_logs, name="read")
logs_command_group.add_command(_archive_logs, name="archive")
