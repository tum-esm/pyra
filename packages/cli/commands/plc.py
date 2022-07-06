import json
import time
from typing import Callable
import click
import os
from packages.core.modules.enclosure_control import CoverError
from packages.core.utils import ConfigInterface, PLCInterface, PLCError
from packages.core.utils import with_filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
CONFIG_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".config.lock")

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))

# TODO: Refactor for new PLC code structure


def get_plc_interface():
    config = ConfigInterface.read()
    plc_interface = None

    try:
        assert config["tum_plc"] is not None, "PLC not configured"
        assert config["tum_plc"]["controlled_by_user"], "PLC is controlled by automation"
        plc_interface = PLCInterface(config)
    except (PLCError, AssertionError) as e:
        error_handler(f"{e}")

    return plc_interface


@click.command(help="Read current state from plc.")
@click.option("--no-indent", is_flag=True, help="Do not print the JSON in an indented manner")
def _read_plc(no_indent):
    plc_interface = get_plc_interface()
    if plc_interface is not None:
        plc_readings = plc_interface.read()
        success_handler(json.dumps(plc_readings.to_dict(), indent=(None if no_indent else 2)))


@click.command(help="Run plc function 'reset()'")
def _write_plc_reset():
    plc_interface = get_plc_interface()
    if plc_interface is not None:
        plc_interface.reset()

        # waiting until reset_needed flag is no longer set
        running_time = 0
        while True:
            time.sleep(2)
            running_time += 2
            if not plc_interface.reset_is_needed():
                break
            assert running_time <= 20, "plc took to long to set reset_needed to false"
        success_handler("Ok")


def wait_until_cover_is_at_angle(plc_interface: PLCInterface, new_cover_angle, timeout=15):
    # waiting until cover is at this angle
    running_time = 0
    while True:
        time.sleep(2)
        running_time += 2
        current_cover_angle = plc_interface.get_cover_angle()
        if abs(new_cover_angle - current_cover_angle) <= 3:
            break

        if running_time > timeout:
            raise CoverError(
                f"Cover took too long to move, latest cover angle: {current_cover_angle}"
            )


@click.command(help="Run plc function 'move_cover()'")
@click.argument("angle")
def _write_plc_move_cover(angle):
    plc_interface = get_plc_interface()
    if plc_interface is not None:
        new_cover_angle = int("".join([c for c in str(angle) if c.isnumeric() or c == "."]))
        assert (new_cover_angle == 0) or (
            new_cover_angle >= 110 and new_cover_angle <= 250
        ), "angle has to be 0° or between 110° and 250°"

        plc_interface.set_manual_control(True)
        plc_interface.set_cover_angle(new_cover_angle)
        plc_interface.set_manual_control(False)
        wait_until_cover_is_at_angle(plc_interface, new_cover_angle)

        success_handler("Ok")


@with_filelock(CONFIG_LOCK_PATH)
def enable_user_control_in_config():
    with open(CONFIG_FILE_PATH, "r") as f:
        config: dict = json.load(f)
    config["tum_plc"]["controlled_by_user"] = True
    with open(CONFIG_FILE_PATH, "w") as f:
        json.dump(config, f)


@click.command(help="Run plc function 'force_cover_close()'")
def _write_plc_close_cover():
    enable_user_control_in_config()

    plc_interface = get_plc_interface()
    if plc_interface is not None:
        plc_interface.set_sync_to_tracker(False)
        plc_interface.set_manual_control(True)
        plc_interface.set_cover_angle(0)
        plc_interface.set_manual_control(False)
        wait_until_cover_is_at_angle(plc_interface, 0)

        success_handler("Ok")


def set_boolean_plc_state(
    state, get_setter_function: Callable[[PLCInterface], Callable[[bool], None]]
):
    plc_interface = get_plc_interface()
    if plc_interface is not None:
        assert state in ["true", "false"], 'state has to be either "true" or "false"'
        get_setter_function(plc_interface)(state == "true")
        success_handler("Ok")


@click.command(help="Run plc function 'set_sync_to_tracker()'")
@click.argument("state")
def _write_plc_sync_to_tracker(state):
    set_boolean_plc_state(state, lambda p: p.set_sync_to_tracker)


@click.command(help="Run plc function 'set_auto_temperature()'")
@click.argument("state")
def _write_plc_auto_temperature(state):
    set_boolean_plc_state(state, lambda p: p.set_auto_temperature)


@click.command(help="Run plc function 'set_power_heater()'")
@click.argument("state")
def _write_plc_power_heater(state):
    set_boolean_plc_state(state, lambda p: p.set_power_heater)


@click.command(help="Run plc function 'set_power_heater()'")
@click.argument("state")
def _write_plc_power_camera(state):
    set_boolean_plc_state(state, lambda p: p.set_power_camera)


@click.command(help="Run plc function 'set_power_router()'")
@click.argument("state")
def _write_plc_power_router(state):
    set_boolean_plc_state(state, lambda p: p.set_power_router)


@click.command(help="Run plc function 'set_power_spectrometer()'")
@click.argument("state")
def _write_plc_power_spectrometer(state):
    set_boolean_plc_state(state, lambda p: p.set_power_spectrometer)


@click.command(help="Run plc function 'set_power_computer()'")
@click.argument("state")
def _write_plc_power_computer(state):
    set_boolean_plc_state(state, lambda p: plc_command_group.set_power_computer)


@click.group()
def plc_command_group():
    pass


plc_command_group.add_command(_read_plc, name="read")
plc_command_group.add_command(_write_plc_reset, name="write-reset")
plc_command_group.add_command(_write_plc_move_cover, name="write-move-cover")
plc_command_group.add_command(_write_plc_close_cover, name="write-close-cover")
plc_command_group.add_command(_write_plc_sync_to_tracker, name="write-sync-to-tracker")
plc_command_group.add_command(_write_plc_auto_temperature, name="write-auto-temperature")
plc_command_group.add_command(_write_plc_power_heater, name="write-power-heater")
plc_command_group.add_command(_write_plc_power_camera, name="write-power-camera")
plc_command_group.add_command(_write_plc_power_router, name="write-power-router")
plc_command_group.add_command(_write_plc_power_spectrometer, name="write-power-spectrometer")
plc_command_group.add_command(_write_plc_power_computer, name="write-power-computer")
