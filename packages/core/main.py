import os
import signal
import sys
import time
from typing import Any

from packages.core import interfaces, threads, types, utils

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

        if any([e.send_emails for e in notified_exceptions]) and (not any([e.send_emails for e in current_exceptions])):
            utils.ExceptionEmailClient.handle_resolved_exception(config)

        state.exceptions_state.notified = state.exceptions_state.current


def run() -> None:
    """The entrypoint of PYRA Core.
    
    Starting with Pyra 4.2.0, the mainloop is only responsible for starting
    and stopping the different threads, and sendinging out emails on occured
    and resolved exceptions. The actual work is done by the threads."""

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

    # Check Python version and platform

    if (not config.general.test_mode) and (sys.platform != "win32"):
        subject = "UnsupportedPlatformError"
        details = f"This function cannot be run on this platform ({sys.platform}). It requires 32-bit Windows."
        logger.error(f"{subject}: {details}")
        return
    if (sys.version_info.major != 3) or (sys.version_info.minor < 10):
        subject = "UnsupportedPythonVersionError"
        details = f"This function requires Python >= 3.10. Current version is {sys.version_info.major}.{sys.version_info.minor}."
        logger.error(f"{subject}: {details}")
        return

    logger.info("Loading astronomical dataset")
    utils.Astronomy.load_astronomical_dataset()

    # these thread classes always exist and start their
    # dedicated mainloop in a parallel thread if the
    # respective service is configured. The threads itself
    # load the config periodically and stop themselves
    logger.info("Initializing threads")
    thread_instances: list[threads.abstract_thread.AbstractThread] = [
        threads.CamTrackerThread(),
        threads.CASThread(),
        threads.HeliosThread(),
        threads.OpusThread(),
        threads.SystemMonitorThread(),
        threads.TUMEnclosureThread(),
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
        logger.debug("Starting iteration")

        interfaces.ActivityHistoryInterface.add_datapoint(
            has_errors=len(state.exceptions_state.current) > 0,
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
        thread_states: list[bool] = []
        for thread_instance in thread_instances:
            r = thread_instance.update_thread_state(config)
            thread_states.append(r)
        if all(thread_states):
            logger.info("All threads are running/pausing correctly")

        if config.general.test_mode:
            logger.debug("pyra-core in test mode")

        # send emails on occured/resolved exceptions
        _send_exception_emails(config)

        # wait rest of loop time
        logger.debug("Finished iteration")
        elapsed_time = time.time() - start_time
        if config.general.test_mode:
            interfaces.ActivityHistoryInterface.dump_current_activity_history()
        time_to_wait = config.general.seconds_per_core_interval - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
