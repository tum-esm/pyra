from datetime import datetime
import json
import os
import time
from filelock import FileLock

from packages.core.logger import Logger
from packages.core.opus_controls import OpusControls
from packages.core.sun_tracking import SunTracking
from packages.core.system_time_sync import SystemTimeSync
from packages.core.validation import Validation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"


def run():
    while True:
        execution_started_at = datetime.now().timestamp()
        Logger.info("Starting Iteration")

        # FileLock = Mark, that the config JSONs are being used and the
        # CLI should not interfere. A file "config/config.lock" will be created
        # and the existence of this file will make the next line wait.
        with FileLock(CONFIG_LOCK_PATH):
            if (not Validation.check_parameters_file()) or (
                not Validation.check_setup_file()
            ):
                # TODO: What to do here?
                time.sleep(60)
                continue

            with open(SETUP_FILE_PATH, "r") as f:
                SETUP = json.load(f)
            with open(PARAMS_FILE_PATH, "r") as f:
                PARAMS = json.load(f)

        # TODO: Stability/system checks
        # TODO: Enclosure communication (rain sensor, ...)
        # TODO: How to group control sequences?

        # TODO: Possibly handle communication between these modules
        # TODO: Pass SETUP and PARAMS to modules

        SystemTimeSync.run()
        SunTracking.run()
        OpusControls.run()

        Logger.info("Ending Iteration")

        # Wait some time so that a certain frequency of the loop is achieved
        execution_ended_at = datetime.now().timestamp()
        time_to_wait = round(
            PARAMS["secondsPerIteration"] - (execution_ended_at - execution_started_at),
            3,
        )
        Logger.debug(f"Waiting {time_to_wait} seconds")
        time.sleep(time_to_wait if time_to_wait > 0 else 0)
