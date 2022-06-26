import json
import time
import click
import os
import sys
from packages.core.modules.enclosure_control import EnclosureControl
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
        error_handler(e)


@click.command(help="Run plc function 'move_cover()'")
@click.argument("angle")
def _write_plc_move_cover(angle):
    try:
        new_cover_angle = int(
            "".join([c for c in str(angle) if c.isnumeric() or c == "."])
        )
        enclosure = get_enclosure()
        enclosure.move_cover(angle)

        # waiting until cover is at this angle
        running_time = 0
        while True:
            time.sleep(2)
            running_time += 2
            if abs(new_cover_angle - enclosure.read_current_cover_angle()) <= 3:
                break
            assert running_time <= 20, "cover took too long to move"

        success_handler("Ok")
    except AssertionError as e:
        error_handler(e)


# TODO: _write_plc_force_cover_close
# TODO: _write_plc_move_cover
# TODO: _write_plc_sync_to_tracker
# TODO: _write_plc_auto_temperature
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
