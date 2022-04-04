import click
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))


error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))

INFO_LOG_FILE = f"{PROJECT_DIR}/logs/info.log"
DEBUG_LOG_FILE = f"{PROJECT_DIR}/logs/debug.log"


@click.command(help="Read the current info.log file.")
def get_info_logs():
    with open(INFO_LOG_FILE, "r") as f:
        click.echo("".join(f.readlines()))


@click.command(help="Read the current debug.log file.")
def get_debug_logs():
    with open(DEBUG_LOG_FILE, "r") as f:
        click.echo("".join(f.readlines()))
