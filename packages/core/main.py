import time
from packages.core import modules
from packages.core.utils import email_client
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
    vbdsd_thread = modules.vbdsd.VBDSD_Thread()

    current_exceptions = []

    while True:
        start_time = time.time()
        logger.info("Starting Iteration")

        try:
            _SETUP, _PARAMS = Config.read()
        except AssertionError:
            # TODO: What to do here?
            time.sleep(60)
            continue

        # Start or stop VBDSD in a thread
        vbdsd_should_be_running = _PARAMS["measurement_triggers"]["type"]["vbdsd"]
        if vbdsd_should_be_running and not vbdsd_thread.is_running():
            vbdsd_thread.start()
        if not vbdsd_should_be_running and vbdsd_thread.is_running():
            vbdsd_thread.stop()

        new_exception = None
        try:
            for module in _modules:
                module.run(_SETUP, _PARAMS)
        except Exception as e:
            new_exception = e

        if new_exception is not None:
            if type(e).__name__ not in current_exceptions:
                current_exceptions.append(type(e).__name__)
                logger.exception(f"Exception {type(e).__name__} has occured.")
                email_client.handle_occured_exception(_SETUP, e)
        else:
            current_exceptions = []
            logger.info(f"All exceptions have been resolved.")
            email_client.handle_resolved_exception(_SETUP)

        logger.info("Ending Iteration")

        # wait rest of loop time
        elapsed_time = time.time() - start_time
        time_to_wait = _PARAMS["pyra"]["seconds_per_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
