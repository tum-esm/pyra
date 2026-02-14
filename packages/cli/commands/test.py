# pyright: reportUnusedFunction=false

import threading
import circadian_scp_upload
import click
import fabric.runners  # pyright: ignore[reportMissingTypeStubs]
import tum_esm_utils

from packages.core import threads, types, utils, interfaces

logger = utils.Logger(origin="cli", lock=None)
state_lock = threading.Lock()


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


@click.group()
def test_command_group() -> None:
    pass


@test_command_group.command(name="opus")
def _test_opus() -> None:
    """Start OPUS, run a macro, stop the macro, close opus."""
    logger.info('running command "test opus"')
    config = types.Config.load()
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )
    try:
        threads.OpusThread.test_setup(config, state_lock, logger)
    finally:
        threads.opus_thread.OpusProgram.stop(logger)
    _print_green("Successfully tested opus connection.")


@test_command_group.command(name="camtracker")
def _test_camtracker() -> None:
    """Start CamTracker, check if it is running, stop CamTracker."""
    logger.info('running command "test camtracker"')
    config = types.Config.load()
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )
    try:
        threads.camtracker_thread.CamTrackerThread.test_setup(config, state_lock, logger)
    finally:
        threads.camtracker_thread.CamTrackerProgram.stop(config, logger)
    _print_green("Successfully tested CamTracker connection.")


@test_command_group.command(name="email")
def _test_emailing() -> None:
    """Send a test email."""
    logger.info('running command "test email"')
    config = types.Config.load()
    utils.ExceptionEmailClient.send_test_email(config)
    _print_green("Successfully sent test email.")


@test_command_group.command(name="upload")
def _test_uploading() -> None:
    """try to connect to upload server."""
    logger.info('running command "test upload"')
    config = types.Config.load()
    if config.upload is None:
        _print_red("No upload server configured.")
        return

    with circadian_scp_upload.client.RemoteConnection(
        config.upload.host.root,
        config.upload.user,
        config.upload.password,
    ) as remote_connection:
        if remote_connection.connection.is_connected:
            _print_green("Successfully connected to upload server")
        else:
            _print_red("Could not connect to upload server")
            exit(1)

        result: fabric.runners.Result

        try:
            result = remote_connection.connection.run("ls ~ > /dev/null 2>&1")
            if result.return_code == 0:
                _print_green("Found home directory of upload user account")
            else:
                raise
        except Exception as e:
            logger.debug(f"Exception: {e}")
            _print_red(
                "Upload user account does not have a home directory, " + 'command "ls ~" failed'
            )
            exit(1)

        try:
            result = remote_connection.connection.run("python3.10 --version > /dev/null 2>&1")
            if result.return_code == 0:
                _print_green("Found Python3.10 installation on upload server")
            else:
                raise
        except Exception as e:
            logger.debug(f"Exception: {e}")
            _print_red(
                "Python3.10 is not installed on upload server, "
                + 'command "python3.10 --version" failed'
            )
            exit(1)
