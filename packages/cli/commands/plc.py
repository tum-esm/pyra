import json
import time
import click
import os
import sys
from packages.core.modules.enclosure_control import CoverError, EnclosureControl
from packages.core.utils.json_interfaces import ConfigInterface

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
STATE_FILE_PATH = os.path.join(PROJECT_DIR, "runtime-data", "state.json")


sys.path.append(PROJECT_DIR)
from packages.core.utils import Validation

error_handler = lambda text: click.echo(click.style(text, fg="red"))
success_handler = lambda text: click.echo(click.style(text, fg="green"))
Validation.logging_handler = error_handler


def get_enclosure():
    _CONFIG = ConfigInterface.read()
    assert not _CONFIG["general"]["test_mode"], "plc not accessible in test mode"
    assert _CONFIG["tum_plc"] is not None, "plc not configured"
    assert _CONFIG["tum_plc"]["controlled_by_user"], "plc is controlled by automation"
    return EnclosureControl(_CONFIG)


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
@click.option(
    "--no-indent", is_flag=True, help="Do not print the JSON in an indented manner"
)
def _read_plc(no_indent):
    try:
        enclosure = get_enclosure()
        plc_readings = enclosure.read_states_from_plc()
        success_handler(json.dumps(plc_readings, indent=(None if no_indent else 2)))
    except AssertionError as e:
        error_handler(e)


@click.command(help="Run plc function 'reset()'")
def _write_plc_reset():
    try:
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
    except AssertionError as e:
        error_handler(f"Failed: {e}")


@click.command(help="Run plc function 'move_cover()'")
@click.argument("angle")
def _write_plc_move_cover(angle):
    try:
        new_cover_angle = int(
            "".join([c for c in str(angle) if c.isnumeric() or c == "."])
        )
        assert (new_cover_angle == 0) or (
            new_cover_angle >= 110 and new_cover_angle <= 250
        ), "angle has to be 0° or between 110° and 250°"

        enclosure = get_enclosure()
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
    except AssertionError as e:
        error_handler(f"Failed: {e}")


@click.command(help="Run plc function 'force_cover_close()'")
def _write_plc_close_cover():
    try:
        enclosure = get_enclosure()
        enclosure.force_cover_close()

        success_handler("Ok")
    except (AssertionError, CoverError) as e:
        error_handler(f"Failed: {e}")


@click.command(help="Run plc function 'set_sync_to_tracker()'")
@click.argument("state")
def _write_plc_sync_to_tracker(state):
    try:
        assert state in ["true", "false"], 'state has to be either "true" or "false"'

        enclosure = get_enclosure()
        enclosure.set_sync_to_tracker(state == "true")

        # TODO: wait until plc state has actually changed
        success_handler("Ok")
    except (AssertionError, CoverError) as e:
        error_handler(f"Failed: {e}")


@click.command(help="Run plc function 'set_auto_temperature()'")
@click.argument("state")
def _write_plc_auto_temperature(state):
    try:
        assert state in ["true", "false"], 'state has to be either "true" or "false"'

        enclosure = get_enclosure()
        enclosure.set_auto_temperature(state == "true")

        # TODO: wait until plc state has actually changed
        success_handler("Ok")
    except (AssertionError, CoverError) as e:
        error_handler(f"Failed: {e}")


# TODO: _write_plc_heater_power
# TODO: _write_plc_camera_power
# TODO: _write_plc_router_power
# TODO: _write_plc_spectrometer_power
# TODO: _write_plc_computer_power


@click.group()
def plc_command_group():
    pass


plc_command_group.add_command(_read_plc, name="read")
plc_command_group.add_command(_write_plc_reset, name="write-reset")
plc_command_group.add_command(_write_plc_move_cover, name="write-move-cover")
plc_command_group.add_command(_write_plc_close_cover, name="write-close-cover")
plc_command_group.add_command(_write_plc_sync_to_tracker, name="sync-to-tracker")
plc_command_group.add_command(_write_plc_auto_temperature, name="auto-temperature")
