import os
import time
from typing import Any, Optional
from packages.core import modules, threads
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
    ExceptionEmailClient,
)

logger = Logger(origin="main")


def update_exception_state(
    config: dict, current_exceptions: list[str], new_exception: Optional[Exception]
) -> list[str]:
    """
    Take a list of current_exceptions (all exceptions that are
    present from the last mainloop iteration, possibly empty) and
    a new_exception (the one that happened in this loop, possibly
    None).

    If the new_exception is None, all exceptions have been resolved
    resolved: send a "resolved" email in case the current_exceptions
    was not empty yet.

    If the new_exception is not None, if it is not already in the
    list of current_exceptions: append it to that list and send a
    "new error occured" email.
    """
    try:
        updated_current_exceptions = [*current_exceptions]
        if new_exception is not None:
            if type(new_exception).__name__ not in current_exceptions:
                updated_current_exceptions.append(type(new_exception).__name__)
                ExceptionEmailClient.handle_occured_exception(config, new_exception)
                if len(current_exceptions) == 0:
                    Logger.log_activity_event("error-occured")
        else:
            if len(current_exceptions) > 0:
                updated_current_exceptions = []
                ExceptionEmailClient.handle_resolved_exception(config)
                logger.info(f"All exceptions have been resolved.")
                Logger.log_activity_event("errors-resolved")

        # if no errors until now
        StateInterface.update({"current_exceptions": current_exceptions}, persistent=True)
        return updated_current_exceptions

    except Exception as e:
        logger.exception(e)
        return current_exceptions


def run() -> None:
    """
    The mainloop of PYRA Core. This function will loop infinitely.
    It loads the config file, validates it runs every module one by
    one, and possibly restarts the upload- and helios-thread.
    """
    StateInterface.initialize()
    logger.info(f"Starting mainloop inside process with PID {os.getpid()}")

    # Loop until a valid config has been found. Without
    # an invalid config, the mainloop cannot initialize
    while True:
        try:
            config = ConfigInterface.read()
            break
        except AssertionError as e:
            logger.error(f"{e}")
            logger.error(f"Invalid config, waiting 10 seconds")
            time.sleep(10)

    # these modules will be executed one by one in each
    # mainloop iteration
    mainloop_modules: Any = [
        modules.measurement_conditions.MeasurementConditions(config),
        modules.enclosure_control.EnclosureControl(config),
        modules.sun_tracking.SunTracking(config),
        modules.opus_measurement.OpusMeasurement(config),
        modules.system_checks.SystemChecks(config),
    ]

    # these thread classes always exist and start their
    # dedicated mainloop in a parallel thread if the
    # respective service is configured. The threads itself
    # load the config periodically and stop themselves
    helios_thread_instance = threads.helios_thread.HeliosThread(config)
    upload_thread_instance = threads.upload_thread.UploadThread(config)

    current_exceptions = StateInterface.read(persistent=True)["current_exceptions"]

    while True:
        start_time = time.time()
        logger.info("Starting iteration")

        # load config at the beginning of each mainloop iteration
        try:
            config = ConfigInterface.read()
        except AssertionError as e:
            logger.error(f"Invalid config, waiting 10 seconds")
            time.sleep(10)
            continue

        # check whether the two threads are (not) running
        # possibly (re)start each thread
        helios_thread_instance.update_thread_state(config)
        upload_thread_instance.update_thread_state(config)

        if config["general"]["test_mode"]:
            logger.info("pyra-core in test mode")
            logger.debug("Skipping HeliosThread and UploadThread in test mode")

        # loop over every module, when one of the modules
        # encounters an exception, this inner loop stops
        # and the exception will be processed (logs, emails)
        new_exception = None
        try:
            for m in mainloop_modules:
                m.run(config)
        except Exception as e:
            new_exception = e
            logger.exception(new_exception)

        # update the list of currently present exceptions
        # send error emails on new exceptions, send resolved
        # emails when no errors are present anymore
        current_exceptions = update_exception_state(config, current_exceptions, new_exception)

        # wait rest of loop time
        logger.info("Ending iteration")
        elapsed_time = time.time() - start_time
        time_to_wait = config["general"]["seconds_per_core_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
