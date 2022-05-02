from datetime import datetime
import json
import os
import time
from filelock import FileLock
import snap7

from packages.core.utils.validation import Validation
from packages.core import modules

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"


from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.main")


def run():

    _modules = [
        modules.measurement_conditions.MeasurementConditions(),
        modules.enclosure_control.EnclosureControl(),
        modules.sun_tracking.SunTracking(),
        modules.opus_measurement.OpusMeasurement(),
    ]

    # TODO: Start vbdsd in a thread

    while True:
        execution_started_at = datetime.now().timestamp()
        logger.info("Starting Iteration")

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
                _SETUP = json.load(f)
            with open(PARAMS_FILE_PATH, "r") as f:
                _PARAMS = json.load(f)

        try:
            for module in _modules:
                module.run(_SETUP, _PARAMS)
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
        time_to_wait = _PARAMS["pyra"]["seconds_per_iteration"] - (
            execution_ended_at - execution_started_at
        )
        time_to_wait = 0 if time_to_wait < 0 else time_to_wait
        logger.debug(f"Waiting {time_to_wait} second(s)")
        time.sleep(time_to_wait)
