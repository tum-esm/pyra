import click
import circadian_scp_upload
from packages.core import types, utils


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.group()
def test_command_group() -> None:
    pass


@test_command_group.command(name="email")
def _test_emailing() -> None:
    """Send a test email."""
    config = types.Config.load()
    utils.ExceptionEmailClient.send_test_email(config)
    _print_green("Successfully sent test email.")


@test_command_group.command(name="upload")
def _test_uploading() -> None:
    """try to connect to upload server."""
    config = types.Config.load()
    if config.upload is None:
        _print_red("No upload server configured.")
        return

    with circadian_scp_upload.RemoteConnection(
        config.upload.host.root,
        config.upload.user,
        config.upload.password,
    ) as remote_connection:
        if remote_connection.connection.is_connected:
            _print_green("Successfully connected to upload server.")
            return

    _print_red("Could not connect to upload server.")
    exit(1)