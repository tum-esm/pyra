import os
import time
from typing import Callable, Literal, Optional
from packages.core import types, utils, interfaces, modules, threads

logger = utils.Logger(origin="main")


def _update_exception_state(
    config: types.ConfigDict,
    current_exceptions: list[str],
    new_exception: Optional[Exception],
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
                utils.ExceptionEmailClient.handle_occured_exception(config, new_exception)
                if len(current_exceptions) == 0:
                    utils.Logger.log_activity_event("error-occured")
        else:
            if len(current_exceptions) > 0:
                updated_current_exceptions = []
                utils.ExceptionEmailClient.handle_resolved_exception(config)
                logger.info(f"All exceptions have been resolved.")
                utils.Logger.log_activity_event("errors-resolved")

        def apply_state_update(
            state: types.PyraCoreStatePersistent,
        ) -> types.PyraCoreStatePersistent:
            state.current_exceptions = updated_current_exceptions
            return state

        interfaces.StateInterface.update_persistent(apply_state_update)
        return updated_current_exceptions

    except Exception as e:
        logger.exception(e)
        return current_exceptions


def run() -> None:
    """The entrypoint of PYRA Core.

    This function infinitely loops over a sequence of modules:

    1. Read the config

    2. Check whether `HeliosThread` and `UploadThread` are running

    3. Possibly start/stop the threads according to the config

    4. Run `MeasurementConditions` module

    5. Run `EnclosureControl` module

    6. Run `SunTracking` module

    7. Run `OpusMeasurement` module

    8. Run `SystemChecks` module

    The mainloop logs all exceptions and sends out emails when new exceptions
    occur and when all exceptions have been resolved.

    **Terminology:** modules are executed one by one in each mainloop iteration.
    Threads are executed in parallel to the mainloop and are started/stopped
    according to the config.
    """

    interfaces.StateInterface.initialize()
    logger.info(f"Starting mainloop inside process with PID {os.getpid()}")

    # Loop until a valid config has been found. Without
    # an invalid config, the mainloop cannot initialize
    while True:
        try:
            config = interfaces.ConfigInterface.read()
            break
        except Exception as e:
            logger.exception(e)
            logger.error("Invalid config, waiting 10 seconds")
            time.sleep(10)

    logger.info("Loading astronomical dataset")
    utils.Astronomy.load_astronomical_dataset()

    # these modules will be executed one by one in each
    # mainloop iteration
    logger.info("Initializing mainloop modules")
    mainloop_modules: list[
        tuple[
            Literal[
                "measurement-conditions",
                "enclosure-control",
                "sun-tracking",
                "opus-measurement",
                "system-checks",
            ],
            Callable[[types.ConfigDict], None],
        ]
    ] = [
        (
            "measurement-conditions",
            modules.measurement_conditions.MeasurementConditions(config).run,
        ),
        ("enclosure-control", modules.enclosure_control.EnclosureControl(config).run),
        ("sun-tracking", modules.sun_tracking.SunTracking(config).run),
        ("opus-measurement", modules.opus_measurement.OpusMeasurement(config).run),
        ("system-checks", modules.system_checks.SystemChecks(config).run),
    ]

    # these thread classes always exist and start their
    # dedicated mainloop in a parallel thread if the
    # respective service is configured. The threads itself
    # load the config periodically and stop themselves
    logger.info("Initializing threads")
    helios_thread_instance = threads.HeliosThread(config)
    upload_thread_instance = threads.UploadThread(config)

    current_exceptions = interfaces.StateInterface.read_persistent().current_exceptions

    while True:
        start_time = time.time()
        logger.info("Starting iteration")

        # load config at the beginning of each mainloop iteration
        try:
            config = interfaces.ConfigInterface.read()
        except Exception as e:
            logger.error("Invalid config, waiting 10 seconds")
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
        for module_name, module_function in mainloop_modules:
            try:
                module_function(config)
            except Exception as e:
                new_exception = e
                logger.exception(new_exception)

                # update the list of currently present exceptions
                # send error emails on new exceptions, send resolved
                # emails when no errors are present anymore
                current_exceptions = _update_exception_state(
                    config, current_exceptions, new_exception
                )
                if module_name == "measurement-conditions":
                    logger.debug(
                        "Skipping remaining modules due to exception in measurement-conditions"
                    )
                    break

        # send resolved email if no exceptions are present anymore
        if new_exception is None:
            current_exceptions = _update_exception_state(config, current_exceptions, None)

        # wait rest of loop time
        logger.info("Ending iteration")
        elapsed_time = time.time() - start_time
        time_to_wait = config["general"]["seconds_per_core_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
