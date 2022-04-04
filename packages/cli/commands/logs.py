import click
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))


@click.command(help="Read the current info.log or debug.log file.")
@click.option("--level", default="INFO", help="Log level INFO or DEBUG")
def _read_logs(level: str):
    assert level in ["INFO", "DEBUG"]
    with open(f"{PROJECT_DIR}/logs/{level.lower()}.log", "r") as f:
        click.echo("".join(f.readlines()))


@click.command(help="Archive the current log files.")
def _archive_logs():
    for filetype in ["info", "debug"]:
        # TODO: Use filelock when writing to logs
        with open(f"{PROJECT_DIR}/logs/{filetype}.log", "r") as f:
            new_log_lines = f.readlines()
        with open(f"{PROJECT_DIR}/logs/{filetype}.log", "w") as f:
            pass
        new_log_date_groups = {}
        for line in new_log_lines:
            date = line[:10]
            if date not in new_log_date_groups.keys():
                new_log_date_groups[date] = []
            new_log_date_groups[date].append(line)

        for date_group, lines in new_log_date_groups.items():
            with open(
                f"{PROJECT_DIR}/logs/archive/{date_group}-{filetype}.log", "a"
            ) as f:
                f.writelines(lines)


@click.group()
def logs_command_group():
    pass


logs_command_group.add_command(_read_logs, name="read")
logs_command_group.add_command(_archive_logs, name="archive")
