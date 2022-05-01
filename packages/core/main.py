from datetime import datetime
import json
import os
import time
import snap7

from packages.core.utils.validation import Validation

from packages.core.modules.opus_measurement import OpusMeasurement
from packages.core.modules.sun_tracking import SunTracking
from packages.core.modules.measurement_conditions import MeasurementConditions
from packages.core.modules.enclosure_control import EnclosureControl

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"


from packages.core.utils.logger import Logger
logger = Logger(origin="pyra.core.main")

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
            # TODO: use traceback?
            print(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} "
                f"of {__file__}: {e}"
            )
            logger.error(e, exc_info=True)
            # TODO: trigger email?

        logger.info("Ending Iteration")
        execution_ended_at = datetime.now().timestamp()
        time_to_wait = PARAMS["pyra"]["seconds_per_iteration"] - (
            execution_ended_at - execution_started_at
        )
        time_to_wait = 0 if time_to_wait < 0 else time_to_wait
        logger.debug(f"Waiting {time_to_wait} second(s)")
        time.sleep(time_to_wait)
