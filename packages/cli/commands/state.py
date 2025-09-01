"""Read the current state.json file."""

import datetime
import os
import threading
import time
import click
import tum_esm_utils

from packages.core import utils, types

logger = utils.Logger(origin="cli", lock=None)
state_lock = threading.Lock()

_PROJECT_DIR = tum_esm_utils.files.rel_to_abs_path("../../..")
_STATE_FILE_PATH = os.path.join(_PROJECT_DIR, "logs", "state.json")


@click.group()
def state_command_group() -> None:
    pass


@state_command_group.command(name="get", help="Read the current state.json file.")
@click.option("--indent", is_flag=True, help="Print the JSON in an indented manner")
def _get_state(indent: bool) -> None:
    logger.debug('running command "state get"')
    state: types.StateObject

    # if state file does not exist, create it
    if not os.path.exists(_STATE_FILE_PATH):
        logger.warning("State file does not exist - Creating new one.")
        state = types.StateObject(last_updated=datetime.datetime.now())
        tum_esm_utils.files.dump_file(_STATE_FILE_PATH, state.model_dump_json(indent=4))

    # otherwise try to load it every 0.2 seconds until it is readable
    else:
        start_time = time.time()
        while True:
            f = tum_esm_utils.files.load_file(_STATE_FILE_PATH)
            try:
                state = types.StateObject.model_validate_json(f)
                break
            except Exception as e:
                time.sleep(0.2)

            if (time.time() - start_time) > 60:
                logger.warning("Could not read state file after 60 seconds - Creating new one.")
                state = types.StateObject(last_updated=datetime.datetime.now())
                tum_esm_utils.files.dump_file(_STATE_FILE_PATH, state.model_dump_json(indent=4))
                break

    click.echo(state.model_dump_json(indent=(2 if indent else None)))
