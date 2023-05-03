"""Interact with the PLC that controls the enclosure hardware."""

import json
import time
from typing import Callable, Optional
import click
import os

import tum_esm_utils
from packages.core import types, utils, interfaces, modules

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_CONFIG_FILE_PATH = os.path.join(_PROJECT_DIR, "config", "config.json")
_CONFIG_LOCK_PATH = os.path.join(_PROJECT_DIR, "config", ".config.lock")


def _print_green(text: str) -> None:
    click.echo(click.style(text, fg="green"))


def _print_red(text: str) -> None:
    click.echo(click.style(text, fg="red"))


def _get_plc_interface() -> Optional[interfaces.PLCInterface]:
    config = interfaces.ConfigInterface.read()
    plc_interface = None

    try:
        assert config["tum_plc"] is not None, "PLC not configured"
        assert config["tum_plc"]["controlled_by_user"], "PLC is controlled by automation"
        plc_interface = interfaces.PLCInterface(
            config["tum_plc"]["version"], config["tum_plc"]["ip"]
        )
        plc_interface.connect()
    except Exception as e:
        _print_red(f"{e}")
        return None

    return plc_interface


@click.command(help="Read current state from plc.")
@click.option("--no-indent", is_flag=True, help="Do not print the JSON in an indented manner")
def _read(no_indent: bool) -> None:
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        plc_readings = plc_interface.read()
        _print_green(json.dumps(plc_readings, indent=(None if no_indent else 2)))
        plc_interface.disconnect()


@click.command(help="Run plc function 'reset()'")
def _reset() -> None:
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        plc_interface.reset()

        # waiting until reset_needed flag is no longer set
        running_time = 0
        while True:
            time.sleep(2)
            running_time += 2
            if not plc_interface.reset_is_needed():
                interfaces.StateInterface.update(
                    {"enclosure_plc_readings": {"state": {"reset_needed": False}}}
                )
                break
            assert running_time <= 20, "plc took to long to set reset_needed to false"
        _print_green("Ok")
        plc_interface.disconnect()


def _wait_until_cover_is_at_angle(
    plc_interface: interfaces.PLCInterface, new_cover_angle: int, timeout: float = 15
) -> None:
    # waiting until cover is at this angle
    running_time = 0
    while True:
        time.sleep(2)
        running_time += 2
        current_cover_angle = plc_interface.get_cover_angle()
        if abs(new_cover_angle - current_cover_angle) <= 3:
            interfaces.StateInterface.update(
                {
                    "enclosure_plc_readings": {
                        "actors": {"current_angle": new_cover_angle},
                        "state": {"cover_closed": new_cover_angle == 0},
                    }
                }
            )
            break

        if running_time > timeout:
            raise modules.enclosure_control.EnclosureControl.CoverError(
                f"Cover took too long to move, latest cover angle: {current_cover_angle}"
            )


@click.command(help="Run plc function 'move_cover()'")
@click.argument("angle")
def _set_cover_angle(angle: str) -> None:
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


@tum_esm_utils.decorators.with_filelock(
    lockfile_path=_CONFIG_FILE_PATH,
    timeout=5,
)
def _enable_user_control_in_config() -> None:
    with open(_CONFIG_FILE_PATH, "r") as f:
        config = json.load(f)
    types.validate_config_dict(config)

    verified_config: types.ConfigDict = config
    if verified_config["tum_plc"] is not None:
        verified_config["tum_plc"]["controlled_by_user"] = True
        with open(_CONFIG_FILE_PATH, "w") as f:
            json.dump(verified_config, f, indent=4)


@click.command(help="Run plc function 'force_cover_close()'")
def _close_cover() -> None:
    _enable_user_control_in_config()

    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        plc_interface.set_sync_to_tracker(False)
        plc_interface.set_manual_control(True)
        plc_interface.set_cover_angle(0)
        plc_interface.set_manual_control(False)
        _wait_until_cover_is_at_angle(plc_interface, 0)

        _print_green("Ok")
        plc_interface.disconnect()


def _set_boolean_plc_state(
    state: str,
    get_setter_function: Callable[[interfaces.PLCInterface], Callable[[bool], None]],
) -> None:
    plc_interface = _get_plc_interface()
    if plc_interface is not None:
        assert state in ["true", "false"], 'state has to be either "true" or "false"'
        get_setter_function(plc_interface)(state == "true")
        _print_green("Ok")
        plc_interface.disconnect()


@click.command(help="Run plc function 'set_sync_to_tracker()'")
@click.argument("state")
def _set_sync_to_tracker(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_sync_to_tracker)


@click.command(help="Run plc function 'set_auto_temperature()'")
@click.argument("state")
def _set_auto_temperature(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_auto_temperature)


@click.command(help="Run plc function 'set_power_heater()'")
@click.argument("state")
def _set_heater_power(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_power_heater)


@click.command(help="Run plc function 'set_power_heater()'")
@click.argument("state")
def _set_camera_power(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_power_camera)


@click.command(help="Run plc function 'set_power_router()'")
@click.argument("state")
def _set_router_power(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_power_router)


@click.command(help="Run plc function 'set_power_spectrometer()'")
@click.argument("state")
def _set_spectrometer_power(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_power_spectrometer)


@click.command(help="Run plc function 'set_power_computer()'")
@click.argument("state")
def _set_computer_power(state: str) -> None:
    _set_boolean_plc_state(state, lambda p: p.set_power_computer)


@click.group()
def plc_command_group() -> None:
    pass


plc_command_group.add_command(_read, name="read")
plc_command_group.add_command(_reset, name="reset")
plc_command_group.add_command(_set_cover_angle, name="set-cover-angle")
plc_command_group.add_command(_close_cover, name="close-cover")
plc_command_group.add_command(_set_sync_to_tracker, name="set-sync-to-tracker")
plc_command_group.add_command(_set_auto_temperature, name="set-auto-temperature")
plc_command_group.add_command(_set_heater_power, name="set-heater-power")
plc_command_group.add_command(_set_camera_power, name="set-camera-power")
plc_command_group.add_command(_set_router_power, name="set-router-power")
plc_command_group.add_command(_set_spectrometer_power, name="set-spectrometer-power")
plc_command_group.add_command(_set_computer_power, name="set-computer-power")
