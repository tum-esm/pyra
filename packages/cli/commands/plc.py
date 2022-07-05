import json
import time
import click
import os
import sys
from packages.core.modules.enclosure_control import EnclosureControl, CoverError, PLCError
from packages.core.utils import ConfigInterface, PLCInterface, PLCError

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")


sys.path.append(PROJECT_DIR)
from packages.core.utils import Validation

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))
Validation.logging_handler = error_handler

# TODO: Refactor for new PLC code structure


def get_enclosure():
    _CONFIG = ConfigInterface.read()
    _CONFIG["general"]["test_mode"] = False
    enclosure = None

    try:
        assert _CONFIG["tum_plc"] is not None, "PLC not configured"
        assert _CONFIG["tum_plc"]["controlled_by_user"], "PLC is controlled by automation"
        enclosure = EnclosureControl(_CONFIG)
        if not enclosure.plc_connect():
            raise PLCError()
    except AssertionError as e:
        error_handler(f"{e}")
    except PLCError:
        error_handler("Could not connect to PLC")

    return enclosure


# TODO: reduced readings: Only the non-toggable properties
# * reset_needed
# * motor_failed
# * cover_is_open
# * rain_detected
# * current_cover_angle
# * temperature
# * fan_speed
# Benefit: Speedup! Only 7 instead of 17 plc-read operations
@click.command(help="Read current state from plc.")
@click.option("--no-indent", is_flag=True, help="Do not print the JSON in an indented manner")
@click.option(
    "--reduced",
    is_flag=True,
    help='Only read the properties "reset_needed", "motor_failed", "cover_is_open", '
    + '"rain_detected", "current_cover_angle", "temperature", "fan_speed"',
)
def _read_plc(no_indent, reduced):
    enclosure = get_enclosure()
    if enclosure is not None:
        plc_readings = enclosure.read_states_from_plc(reduced=reduced)
        success_handler(json.dumps(plc_readings, indent=(None if no_indent else 2)))


@click.command(help="Run plc function 'reset()'")
def _write_plc_reset():
    enclosure = get_enclosure()
    if enclosure is not None:
        enclosure = get_enclosure()
        enclosure.reset()

        # waiting until reset_needed flag is no longer set
        running_time = 0
        while True:
            time.sleep(2)
            running_time += 2
            if not enclosure.check_for_reset_needed():
                break
            assert running_time <= 20, "plc took to long to set reset_needed to false"
        success_handler("Ok")


@click.command(help="Run plc function 'move_cover()'")
@click.argument("angle")
def _write_plc_move_cover(angle):
    enclosure = get_enclosure()
    if enclosure is not None:
        new_cover_angle = int("".join([c for c in str(angle) if c.isnumeric() or c == "."]))
        assert (new_cover_angle == 0) or (
            new_cover_angle >= 110 and new_cover_angle <= 250
        ), "angle has to be 0° or between 110° and 250°"

        enclosure.move_cover(angle)

        # waiting until cover is at this angle
        running_time = 0
        while True:
            time.sleep(2)
            running_time += 2
            current_cover_angle = enclosure.read_current_cover_angle()
            if abs(new_cover_angle - current_cover_angle) <= 3:
                break
            assert (
                running_time <= 20
            ), f"Cover took too long to move, latest cover angle: {current_cover_angle}"

        success_handler("Ok")


@click.command(help="Run plc function 'force_cover_close()'")
def _write_plc_close_cover():
    enclosure = get_enclosure()
    if enclosure is not None:
        # TODO: set controlled_by_user to true
        enclosure.force_cover_close()
        success_handler("Ok")


def set_boolean_plc_state(state, setResolver):
    enclosure = get_enclosure()
    if enclosure is not None:
        assert state in ["true", "false"], 'state has to be either "true" or "false"'
        setResolver(enclosure)(state == "true")
        # TODO: Make sure that plc state has actually changed (inside enclosure code)
        success_handler("Ok")


@click.command(help="Run plc function 'set_sync_to_tracker()'")
@click.argument("state")
def _write_plc_sync_to_tracker(state):
    set_boolean_plc_state(state, lambda e: e.set_sync_to_tracker)


@click.command(help="Run plc function 'set_auto_temperature()'")
@click.argument("state")
def _write_plc_auto_temperature(state):
    set_boolean_plc_state(state, lambda e: e.set_auto_temperature)


@click.command(help="Run plc function 'set_power_heater()'")
@click.argument("state")
def _write_plc_power_heater(state):
    set_boolean_plc_state(state, lambda e: e.set_power_heater)


@click.command(help="Run plc function 'set_power_heater()'")
@click.argument("state")
def _write_plc_power_camera(state):
    set_boolean_plc_state(state, lambda e: e.set_power_camera)


@click.command(help="Run plc function 'set_power_router()'")
@click.argument("state")
def _write_plc_power_router(state):
    set_boolean_plc_state(state, lambda e: e.set_power_router)


@click.command(help="Run plc function 'set_power_spectrometer()'")
@click.argument("state")
def _write_plc_power_spectrometer(state):
    set_boolean_plc_state(state, lambda e: e.set_power_spectrometer)


@click.command(help="Run plc function 'set_power_computer()'")
@click.argument("state")
def _write_plc_power_computer(state):
    set_boolean_plc_state(state, lambda e: e.set_power_computer)


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
