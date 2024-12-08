"""Interact with the PLC that controls the enclosure hardware."""

import json
import time
from typing import Callable, Literal, Optional
import click
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="cli")


@click.group(name="tum-enclosure")
def tum_enclosure_command_group() -> None:
    pass


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


def _get_plc_interface() -> Optional[interfaces.TUMEnclosureInterface]:
    config = types.Config.load()
    plc_interface = None

    try:
        assert config.tum_enclosure is not None, "PLC not configured"
        assert config.tum_enclosure.controlled_by_user, "PLC is controlled by automation"
        plc_interface = interfaces.TUMEnclosureInterface(
            config.tum_enclosure.version, config.tum_enclosure.ip
        )
        plc_interface.connect()
    except Exception as e:
        _print_red(str(e))
        exit(1)

    return plc_interface


@tum_enclosure_command_group.command(
    name="read",
    help="Read current state from plc.",
)
@click.option("--no-indent", is_flag=True, help="Do not print the JSON in an indented manner")
def _read(no_indent: bool) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info('running command "plc read"')
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        plc_readings = plc_interface.read()
        _print_green(json.dumps(plc_readings, indent=(None if no_indent else 2)))
        plc_interface.disconnect()


@tum_enclosure_command_group.command(
    name="reset",
    help="Run plc function 'reset()'",
)
def _reset() -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info('running command "plc reset"')
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        plc_interface.reset()

        # waiting until reset_needed flag is no longer set
        running_time = 0
        while True:
            time.sleep(2)
            running_time += 2
            if not plc_interface.reset_is_needed():
                with interfaces.StateInterface.update_state() as state:
                    if state.tum_enclosure_state is not None:
                        state.tum_enclosure_state.state.reset_needed = False
                break
            assert running_time <= 20, "plc took to long to set reset_needed to false"
        _print_green("Ok")
        plc_interface.disconnect()


def _wait_until_cover_is_at_angle(
    plc_interface: interfaces.TUMEnclosureInterface,
    new_cover_angle: int,
    timeout: float = 15
) -> None:
    # waiting until cover is at this angle
    running_time = 0
    while True:
        time.sleep(2)
        running_time += 2
        current_cover_angle = plc_interface.get_cover_angle()
        if abs(new_cover_angle - current_cover_angle) <= 3:
            with interfaces.StateInterface.update_state() as state:
                state.tum_enclosure_state.actors.current_angle = current_cover_angle
                state.tum_enclosure_state.state.cover_closed = (current_cover_angle == 0)
            break

        if running_time > timeout:
            raise modules.enclosure_control.EnclosureControl.CoverError(
                f"Cover took too long to move, latest cover angle: {current_cover_angle}"
            )


@tum_enclosure_command_group.command(
    name="set-cover-angle",
    help="Run plc function 'move_cover()'",
)
@click.argument("angle")
def _set_cover_angle(angle: str) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-cover-angle {angle}"')
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        new_cover_angle = int("".join([c for c in str(angle) if c.isnumeric() or c == "."]))
        assert (new_cover_angle == 0) or (
            new_cover_angle >= 110 and new_cover_angle <= 250
        ), "angle has to be 0° or between 110° and 250°"

        plc_interface.set_manual_control(True)
        plc_interface.set_sync_to_tracker(False)
        plc_interface.set_cover_angle(new_cover_angle)
        plc_interface.set_manual_control(False)
        _wait_until_cover_is_at_angle(plc_interface, new_cover_angle)

        _print_green("Ok")
        plc_interface.disconnect()


@tum_enclosure_command_group.command(
    name="close-cover",
    help="Run plc function 'force_cover_close()'",
)
def _close_cover() -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info('running command "plc close-cover"')
    with types.Config.update_in_context() as config:
        assert config.tum_enclosure is not None, "PLC not configured"
        config.tum_enclosure.controlled_by_user = True
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        plc_interface.set_sync_to_tracker(False)
        plc_interface.set_manual_control(True)
        plc_interface.set_cover_angle(0)
        plc_interface.set_manual_control(False)
        _wait_until_cover_is_at_angle(plc_interface, 0)

        _print_green("Ok")
        plc_interface.disconnect()


def _set_boolean_tum_enclosure_state(
    state: Literal["true", "false"],
    get_setter_function: Callable[[interfaces.TUMEnclosureInterface], Callable[[bool], None]],
) -> None:
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        assert state in ["true", "false"], 'state has to be either "true" or "false"'
        get_setter_function(plc_interface)(state == "true")
        _print_green("Ok")
        plc_interface.disconnect()


@tum_enclosure_command_group.command(
    name="set-sync-to-tracker",
    help="Run plc function 'set_sync_to_tracker()'",
)
@click.argument("state")
def _set_sync_to_tracker(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-sync-to-tracker {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_sync_to_tracker)


@tum_enclosure_command_group.command(
    name="set-auto-temperature",
    help="Run plc function 'set_auto_temperature()'",
)
@click.argument("state")
def _set_auto_temperature(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-auto-temperature {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_auto_temperature)


@tum_enclosure_command_group.command(
    name="set-heater-power",
    help="Run plc function 'set_power_heater()'",
)
@click.argument("state")
def _set_heater_power(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-heater-power {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_power_heater)


@tum_enclosure_command_group.command(
    name="set-camera-power",
    help="Run plc function 'set_camera_heater()'",
)
@click.argument("state")
def _set_camera_power(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-camera-power {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_power_camera)


@tum_enclosure_command_group.command(
    name="set-router-power",
    help="Run plc function 'set_power_router()'",
)
@click.argument("state")
def _set_router_power(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-router-power {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_power_router)


@tum_enclosure_command_group.command(
    name="set-spectrometer-power",
    help="Run plc function 'set_power_spectrometer()'",
)
@click.argument("state")
def _set_spectrometer_power(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-spectrometer-power {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_power_spectrometer)


@tum_enclosure_command_group.command(
    name="set-computer-power",
    help="Run plc function 'set_power_computer()'",
)
@click.argument("state")
def _set_computer_power(state: Literal["true", "false"]) -> None:
    with interfaces.StateInterface.update_state() as s:
        s.recent_cli_calls += 1
    logger.info(f'running command "plc set-computer-power {state}"')
    _set_boolean_tum_enclosure_state(state, lambda p: p.set_power_computer)
