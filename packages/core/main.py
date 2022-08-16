import os
import time
from packages.core import modules, threads
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
    ExceptionEmailClient,
)

logger = Logger(origin="main")

# TODO: document
def update_exception_state(
    config: dict, current_exceptions: list[str], new_exception: Exception
):
    try:
        new_current_exceptions = [*current_exceptions]

        if new_exception is not None:
            if type(new_exception).__name__ not in current_exceptions:
                new_current_exceptions.append(type(new_exception).__name__)
                ExceptionEmailClient.handle_occured_exception(config, new_exception)
                if len(current_exceptions) == 0:
                    Logger.log_activity_event("error-occured")
        else:
            if len(current_exceptions) > 0:
                new_current_exceptions = []
                ExceptionEmailClient.handle_resolved_exception(config)
                logger.info(f"All exceptions have been resolved.")
                Logger.log_activity_event("errors-resolved")

        # if no errors until now
        current_exceptions = [*new_current_exceptions]
        StateInterface.update({"current_exceptions": current_exceptions}, persistent=True)
    except Exception as e:
        logger.exception(e)

    return current_exceptions


def run():
    StateInterface.initialize()
    logger.info(f"Starting mainloop inside process with PID {os.getpid()}")

    while True:
        try:
            _CONFIG = ConfigInterface.read()
            break
        except AssertionError as e:
            logger.error(f"{e}")
            logger.error(f"Invalid config, waiting 10 seconds")
            time.sleep(10)

    _modules = [
        modules.measurement_conditions.MeasurementConditions(_CONFIG),
        modules.enclosure_control.EnclosureControl(_CONFIG),
        modules.sun_tracking.SunTracking(_CONFIG),
        modules.opus_measurement.OpusMeasurement(_CONFIG),
        modules.system_checks.SystemChecks(_CONFIG),
    ]
    helios_thread_instance = threads.helios_thread.HeliosThread()
    upload_thread_instance = threads.upload_thread.UploadThread()

    current_exceptions = StateInterface.read(persistent=True)["current_exceptions"]

    while True:
        start_time = time.time()
        logger.info("Starting iteration")

        try:
            _CONFIG = ConfigInterface.read()
        except AssertionError as e:
            logger.error(f"Invalid config, waiting 10 seconds")
            time.sleep(10)
            continue

        # check whether the two threads are (not) running
        # possibly (re)start each thread
        helios_thread_instance.update_thread_state()
        upload_thread_instance.update_thread_state()

        if _CONFIG["general"]["test_mode"]:
            logger.info("pyra-core in test mode")
            logger.debug("Skipping HeliosThread and UploadThread in test mode")

        new_exception = None
        try:
            for module in _modules:
                module.run(_CONFIG)
        except Exception as e:
            new_exception = e
            logger.exception(new_exception)

        # update the list of currently present exceptions
        # send error emails on new exceptions, send resolved
        # emails when no errors are present anymore
        current_exceptions = update_exception_state(_CONFIG, current_exceptions, new_exception)

        # wait rest of loop time
        logger.info("Ending iteration")
        elapsed_time = time.time() - start_time
        time_to_wait = _CONFIG["general"]["seconds_per_core_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
