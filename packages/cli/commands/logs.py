import click
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))

INFO_LOG_FILE = f"{PROJECT_DIR}/logs/info.log"
DEBUG_LOG_FILE = f"{PROJECT_DIR}/logs/debug.log"


@click.command(help="Read the current info.log or debug.log file.")
@click.option("--level", default="INFO", help="Log level INFO or DEBUG")
def _read_logs(level: str):
    with open(DEBUG_LOG_FILE if level == "DEBUG" else INFO_LOG_FILE, "r") as f:
        click.echo("".join(f.readlines()))


@click.group()
def logs_command_group():
    pass


logs_command_group.add_command(_read_logs, name="read")
