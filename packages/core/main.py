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


def load_config():
    # FileLock = Mark, that the config JSONs are being used and the
    # CLI should not interfere. A file "config/config.lock" will be created
    # and the existence of this file will make the next line wait.
    with FileLock(CONFIG_LOCK_PATH):
        assert (Validation.check_parameters_file() and Validation.check_setup_file())

        with open(SETUP_FILE_PATH, "r") as f:
            _SETUP = json.load(f)
        with open(PARAMS_FILE_PATH, "r") as f:
            _PARAMS = json.load(f)
    return _SETUP, _PARAMS



def run():

    _SETUP, _PARAMS = load_config()

    _modules = [
        modules.measurement_conditions.MeasurementConditions(_SETUP, _PARAMS),
        modules.enclosure_control.EnclosureControl(_SETUP, _PARAMS),
        modules.sun_tracking.SunTracking(_SETUP, _PARAMS),
        modules.opus_measurement.OpusMeasurement(_SETUP, _PARAMS),
    ]

    # TODO: Start vbdsd in a thread

    while True:
        execution_started_at = datetime.now().timestamp()
        logger.info("Starting Iteration")

        try:
            _SETUP, _PARAMS = load_config()
        except AssertionError:
            # TODO: What to do here?
                time.sleep(60)
                continue

        try:
            for module in _modules:
                module.run(_SETUP, _PARAMS)
        except snap7.snap7exceptions.Snap7Exception:
            logger.exception("An exception was thrown!")
        except Exception as e:
            logger.exception("An exception was thrown!")
            print(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} "
                f"of {__file__}: {e}"
            )
            # TODO: trigger email?

        logger.info("Ending Iteration")
        execution_ended_at = datetime.now().timestamp()
        time_to_wait = _PARAMS["pyra"]["seconds_per_iteration"] - (
            execution_ended_at - execution_started_at
        )
        time_to_wait = 0 if time_to_wait < 0 else time_to_wait
        logger.debug(f"Waiting {time_to_wait} second(s)")
        time.sleep(time_to_wait)
