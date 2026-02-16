"""Interact with the PLC that controls the enclosure hardware."""

# pyright: reportUnusedFunction=false

import json
from typing import Literal

import click
import tum_esm_utils

from packages.core import interfaces, types, utils

logger = utils.Logger(origin="cli", lock=None)


@click.group(name="aemet-enclosure")
def aemet_enclosure_command_group() -> None:
    pass


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


def _get_enclosure_interface() -> interfaces.AEMETEnclosureInterface:
    config = types.Config.load()
    interface = None
    state_lock = tum_esm_utils.sqlitelock.SQLiteLock(
        filepath=interfaces.state_interface.STATE_LOCK_PATH,
        timeout=interfaces.state_interface.STATE_LOCK_TIMEOUT,
        poll_interval=interfaces.state_interface.STATE_LOCK_POLL_INTERVAL,
    )

    try:
        assert config.aemet_enclosure is not None, "PLC not configured"
        assert config.aemet_enclosure.controlled_by_user, "Enclosure is controlled by automation"
        interface = interfaces.AEMETEnclosureInterface(
            config=config.aemet_enclosure,
            state_lock=state_lock,
            logger=logger,
        )
    except Exception as e:
        _print_red(str(e))
        exit(1)

    return interface


@aemet_enclosure_command_group.command(
    name="read",
    help="Read current state from plc.",
)
@click.option("--no-indent", is_flag=True, help="Do not print the JSON in an indented manner")
def _read(no_indent: bool) -> None:
    logger.debug('running command "plc read"')
    interface = _get_enclosure_interface()
    _print_green(json.dumps(interface.read(), indent=(None if no_indent else 2)))


@aemet_enclosure_command_group.command(name="open-cover", help="Open the cover of the enclosure")
def _open_cover() -> None:
    logger.info('running command "plc open-cover"')
    with types.Config.update_in_context() as config:
        assert config.aemet_enclosure is not None, "PLC not configured"
        config.aemet_enclosure.controlled_by_user = True
    interface = _get_enclosure_interface()
    interface.open_cover()
    _print_green("Ok")


@aemet_enclosure_command_group.command(name="close-cover", help="Close the cover of the enclosure")
def _close_cover() -> None:
    logger.info('running command "plc close-cover"')
    with types.Config.update_in_context() as config:
        assert config.aemet_enclosure is not None, "PLC not configured"
        config.aemet_enclosure.controlled_by_user = True
    interface = _get_enclosure_interface()
    interface.close_cover()
    _print_green("Ok")


@aemet_enclosure_command_group.command(
    name="set-spectrometer-power",
    help="Run plc function 'set_power_spectrometer()'",
)
@click.argument("state")
def _set_spectrometer_power(state: Literal["true", "false"]) -> None:
    logger.info(f'running command "plc set-spectrometer-power {state}"')
    enclosure_interface = _get_enclosure_interface()
    enclosure_interface.set_em27_power(state == "true")
    _print_green("Ok")


@aemet_enclosure_command_group.command(
    name="set-enhanced-security-mode",
    help="Set the variable ENHANCED_SECURITY to 1 (true) or 0 (false).",
)
@click.argument("value")
def _set_enhance_security_mode(value: int) -> None:
    logger.info(f'running command "plc set-enhance-security-mode {value}"')
    enclosure_interface = _get_enclosure_interface()
    enclosure_interface.set_enhanced_security_mode(int(value) == 1)
    _print_green("Ok")


@aemet_enclosure_command_group.command(
    name="set-averia-fault-code",
    help="Set the variable AVERIA to a given integer value.",
)
@click.argument("value")
def _set_averia_fault_code(value: int) -> None:
    logger.info(f'running command "plc set-averia-fault-code {value}"')
    enclosure_interface = _get_enclosure_interface()
    enclosure_interface.set_averia_fault_code(int(value))
    _print_green("Ok")


@aemet_enclosure_command_group.command(
    name="set-alert-level",
    help="Set the variable ALERTA to a given integer value.",
)
@click.argument("value")
def _set_alert_level(value: int) -> None:
    logger.info(f'running command "plc set-alert-level {value}"')
    enclosure_interface = _get_enclosure_interface()
    enclosure_interface.set_alert_level(int(value))
    _print_green("Ok")


@aemet_enclosure_command_group.command(
    name="set-auto-mode",
    help="Set the variable AUTO to a given integer value.",
)
@click.argument("value")
def _set_auto_mode(value: int) -> None:
    logger.info(f'running command "plc set-auto-mode {value}"')
    enclosure_interface = _get_enclosure_interface()
    enclosure_interface.set_enclosure_mode("auto" if int(value) == 1 else "manual")
    _print_green("Ok")
