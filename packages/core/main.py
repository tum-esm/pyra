import os
import time
from packages.core import modules
from packages.core.utils import email_client
from packages.core.utils import ConfigInterface, StateInterface, Logger


# TODO: Figure out, where the program could get stuck. In the end,
# everything should be logged to the log files and no exception
# should go missing


def run():

    logger = Logger(origin="pyra.core.main")

    StateInterface.initialize()
    _CONFIG = ConfigInterface.read()

    _modules = [
        modules.measurement_conditions.MeasurementConditions(_CONFIG),
        modules.enclosure_control.EnclosureControl(_CONFIG),
        modules.sun_tracking.SunTracking(_CONFIG),
        modules.opus_measurement.OpusMeasurement(_CONFIG),
    ]
    vbdsd_thread = modules.vbdsd.VBDSD_Thread()

    current_exceptions = []

    while True:
        start_time = time.time()
        logger.info("Starting Iteration")

        try:
            _CONFIG = ConfigInterface.read()
        except AssertionError:
            time.sleep(30)
            continue

        # Start or stop VBDSD in a thread
        vbdsd_should_be_running = _CONFIG["measurement_triggers"]["consider_vbdsd"]
        if vbdsd_should_be_running and not vbdsd_thread.is_running():
            vbdsd_thread.start()
        if not vbdsd_should_be_running and vbdsd_thread.is_running():
            vbdsd_thread.stop()

        new_exception = None
        try:
            for module in _modules:
                module.run(_CONFIG)
        except Exception as e:
            new_exception = e

        try:
            new_current_exceptions = [*current_exceptions]

            if new_exception is not None:
                if type(e).__name__ not in current_exceptions:
                    new_current_exceptions.append(type(e).__name__)
                    email_client.handle_occured_exception(_CONFIG["error_email"], e)
                    logger.exception(f"Exception {type(e).__name__} has occured.")
            else:
                if len(current_exceptions) > 0:
                    new_current_exceptions = []
                    email_client.handle_resolved_exception(_CONFIG["error_email"])
                    logger.info(f"All exceptions have been resolved.")

            # if no errors until now
            current_exceptions = [*new_current_exceptions]
        except Exception as e:
            logger.exception(f"Exception {type(e).__name__} during email sending.")

        logger.info("Ending Iteration")

        # wait rest of loop time
        elapsed_time = time.time() - start_time
        time_to_wait = _CONFIG["general"]["seconds_per_core_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
