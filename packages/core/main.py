from datetime import datetime
import json
import logging
import os
import time
import snap7

from packages.core.opus_measurement import OpusMeasurement
from packages.core.sun_tracking import SunTracking
from packages.core.measurement_conditions import MeasurementConditions
from packages.core.enclosure_control import EnclosureControl
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

        try:
            # TODO: lock config and parameter files during read operation
            Validation.check_parameters_config()
            Validation.check_setup_config()
            with open(SETUP_FILE_PATH, "r") as f:
                SETUP = json.load(f)
            with open(PARAMS_FILE_PATH, "r") as f:
                PARAMS = json.load(f)

            # TODO: Possibly handle communication between these modules
            MeasurementConditions.set_config = (SETUP, PARAMS)
            MeasurementConditions.run()
            EnclosureControl.set_config = (SETUP, PARAMS)
            EnclosureControl.run()
            SunTracking.set_config = (SETUP, PARAMS)
            SunTracking.run()
            OpusMeasurement.set_config = (SETUP, PARAMS)
            OpusMeasurement.run()
        except snap7.snap7exceptions.Snap7Exception:
            pass
        except Exception as e:
            #TODO: use traceback?
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} "
                  f"of {__file__}: {e}")
            logger.error(e, exc_info=True)
            #TODO: trigger email?

        logger.info("Ending Iteration")
        execution_ended_at = datetime.now().timestamp()
        time_to_wait = PARAMS["pyra"]["seconds_per_iteration"] - (
            execution_ended_at - execution_started_at
        )
        time_to_wait = 0 if time_to_wait < 0 else time_to_wait
        logger.debug(f"Waiting {time_to_wait} second(s)")
        time.sleep(time_to_wait)
