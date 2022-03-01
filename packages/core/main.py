from datetime import datetime
import json
import os
import time

from packages.core.opus_measurement import OpusMeasurement
from packages.core.sun_tracking import SunTracking
from packages.core.system_time_sync import SystemTimeSync
from packages.core.validation import Validation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"

# TODO: Setup logging module (logging to file)


def run():
    while True:
        execution_started_at = datetime.now().timestamp()

        # TODO: lock config and parameter files during read operation
        Validation.check_parameters_config()
        Validation.check_setup_config()
        with open(SETUP_FILE_PATH, "r") as f:
            SETUP = json.load(f)
        with open(PARAMS_FILE_PATH, "r") as f:
            PARAMS = json.load(f)

        # TODO: Do pyra stuff
        SystemTimeSync.run()
        SunTracking.run()
        OpusMeasurement.run()

        execution_ended_at = datetime.now().timestamp()
        time_to_wait = PARAMS["secondsPerIteration"] - (
            execution_ended_at - execution_started_at
        )
        if time_to_wait > 0:
            time.sleep(time_to_wait)
