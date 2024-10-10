import os
import signal
import time
from typing import Any, Callable, Literal
from packages.core import types, utils, interfaces, modules, threads

logger = utils.Logger(origin="main")


def _send_exception_emails(config: types.Config) -> None:
    """Send emails on occured/resolved exceptions."""

    with interfaces.StateInterface.update_state() as state:
        current_exceptions = state.exceptions_state.current
        notified_exceptions = state.exceptions_state.notified

        new_exception_emails = [
            e for e in current_exceptions if ((e not in notified_exceptions) and e.send_emails)
        ]
        if len(new_exception_emails) > 0:
            utils.ExceptionEmailClient.handle_occured_exceptions(config, new_exception_emails)

        if not any([e.send_emails for e in current_exceptions]):
            utils.ExceptionEmailClient.handle_resolved_exception(config)

        state.exceptions_state.notified = state.exceptions_state.current


def run() -> None:
    """The entrypoint of PYRA Core.

    This function infinitely loops over a sequence of modules:

    1. Read the config

    2. Check whether `HeliosThread`, `SystemChecksThread`, and `UploadThread` are running

    3. Possibly start/stop the threads according to the config

    4. Run `MeasurementConditions` module

    5. Run `EnclosureControl` module

    6. Run `SunTracking` module

    7. Run `OpusMeasurement` module

    The mainloop logs all exceptions and sends out emails when new exceptions
    occur and when all exceptions have been resolved.

    **Terminology:** modules are executed one by one in each mainloop iteration.
    Threads are executed in parallel to the mainloop and are started/stopped
    according to the config.
    """

    logger.info(f"Starting mainloop inside process with process ID {os.getpid()}")

    # Loop until a valid config has been found. Without
    # an invalid config, the mainloop cannot initialize
    while True:
        try:
            config = types.Config.load()
            break
        except ValueError as e:
            logger.error(
                "Invalid config, waiting 10 seconds: " + str(e).replace("Config is invalid:", "")
            )
            time.sleep(10)
        except Exception as e:
            logger.exception(e)
            logger.error("Could not load config, waiting 10 seconds")
            time.sleep(10)

    logger.info("Loading astronomical dataset")
    utils.Astronomy.load_astronomical_dataset()

    # these modules will be executed one by one in each
    # mainloop iteration
    logger.info("Initializing mainloop modules")
    mainloop_modules: list[tuple[
        Literal[
            "enclosure-control",
        ],
        Callable[[types.Config], None],
    ]] = [
        ("enclosure-control", modules.enclosure_control.EnclosureControl(config).run),
    ]

    # these thread classes always exist and start their
    # dedicated mainloop in a parallel thread if the
    # respective service is configured. The threads itself
    # load the config periodically and stop themselves
    logger.info("Initializing threads")
    thread_instances: list[threads.abstract_thread.AbstractThread] = [
        threads.CamTrackerThread(),
        threads.HeliosThread(),
        threads.CASThread(),
        threads.OpusThread(),
        threads.SystemChecksThread(),
        threads.UploadThread(),
    ]

    logger.info("Removing temporary state from previous runs")
    with interfaces.StateInterface.update_state() as state:
        state.reset()

    # Before shutting down: save the current activity history and log
    # that the core is shutting down
    def _graceful_teardown(*args: Any) -> None:
        logger.info("Received shutdown signal, starting graceful teardown")
        interfaces.ActivityHistoryInterface.dump_current_activity_history()
        with interfaces.StateInterface.update_state() as state:
            state.reset()
        logger.info("Graceful teardown complete")
        exit(0)

    signal.signal(signal.SIGINT, _graceful_teardown)
    signal.signal(signal.SIGTERM, _graceful_teardown)
    logger.info("Established graceful teardown hook")

    while True:
        start_time = time.time()
        logger.info("Starting iteration")

        interfaces.ActivityHistoryInterface.add_datapoint(
            has_errors=len(state.current_exceptions) > 0,
        )

        # load config at the beginning of each mainloop iteration
        try:
            config = types.Config.load()
        except ValueError as e:
            logger.error(
                "Invalid config, waiting 10 seconds: " + str(e).replace("Config is invalid:", "")
            )
            time.sleep(10)
            continue
        except Exception as e:
            logger.exception(e)
            logger.error("Invalid config, waiting 10 seconds")
            time.sleep(10)
            continue

        # check whether the threads are running and possibly (re)start them
        for thread_instance in thread_instances:
            thread_instance.update_thread_state(config)

        if config.general.test_mode:
            logger.info("pyra-core in test mode")
            logger.debug("Skipping HeliosThread and UploadThread in test mode")

        # loop over every module, when one of the modules
        # encounters an exception, this inner loop stops
        # and the exception will be processed (logs, emails)
        new_exception = None
        for module_name, module_function in mainloop_modules:
            try:
                module_function(config)
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.clear_exception_origin(module_name)
            except Exception as e:
                new_exception = e
                logger.exception(new_exception)

                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.add_exception(origin=module_name, exception=e)

        # send emails on occured/resolved exceptions
        _send_exception_emails(config)

        # wait rest of loop time
        logger.info("Ending iteration")
        elapsed_time = time.time() - start_time
        seconds_per_core_interval = config.general.seconds_per_core_interval
        if config.general.test_mode:
            seconds_per_core_interval = 10
            interfaces.ActivityHistoryInterface.dump_current_activity_history()
        time_to_wait = seconds_per_core_interval - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
