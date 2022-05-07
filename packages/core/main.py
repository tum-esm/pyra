from datetime import datetime
import time
import snap7

from packages.core import modules
from packages.core.utils.json_file_interaction import State, Config
from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.main")


def run():

    State.initialize()

    _SETUP, _PARAMS = Config.read()
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
            _SETUP, _PARAMS = Config.read()
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
