import json
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
    _CONFIG = ConfigInterface.read()

    if _CONFIG["general"]["test_mode"]:
        error_handler("plc not accessible in test mode")
        return

    if _CONFIG["tum_plc"] is None:
        error_handler("plc not configured")
        return

    enclosure = EnclosureControl(ConfigInterface.read())
    plc_readings = enclosure.read_states_from_plc()
    success_handler(json.dumps(plc_readings, indent=(None if no_indent else 2)))


# TODO: _write_plc_reset
# TODO: _write_plc_force_cover_close
# TODO: _write_plc_move_to_angle
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
