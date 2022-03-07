from datetime import datetime
import json
import logging
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

# Setup logging module
logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.DEBUG, filename="logs/debug.log", format=logging_format
)

logging_info_handler = logging.FileHandler(filename="logs/info.log", mode="a")
logging_info_handler.setLevel(logging.INFO)
logging_info_handler.setFormatter(logging.Formatter(logging_format))

logger = logging.getLogger("pyra.core")
logger.addHandler(logging_info_handler)

# https://docs.python.org/3/howto/logging.html#handlers


def run():
    while True:
        execution_started_at = datetime.now().timestamp()
        logger.info("Starting Iteration")

        # TODO: lock config and parameter files during read operation
        Validation.check_parameters_config()
        Validation.check_setup_config()
        with open(SETUP_FILE_PATH, "r") as f:
            SETUP = json.load(f)
        with open(PARAMS_FILE_PATH, "r") as f:
            PARAMS = json.load(f)

        # TODO: Possibly handle communication between these modules
        # TODO: Pass SETUP and PARAMS to modules
        SystemTimeSync.run()
        SunTracking.run()
        OpusMeasurement.run(SETUP, PARAMS)

        logger.info("Ending Iteration")
        execution_ended_at = datetime.now().timestamp()
        time_to_wait = PARAMS["secondsPerIteration"] - (
            execution_ended_at - execution_started_at
        )
        time_to_wait = 0 if time_to_wait < 0 else time_to_wait
        logger.debug(f"Waiting {time_to_wait} second(s)")
        time.sleep(time_to_wait)
