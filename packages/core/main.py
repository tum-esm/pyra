import os
import time
from packages.core import modules
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
    ExceptionEmailClient,
)


# TODO: Figure out, where the program could get stuck. In the end,
# everything should be logged to the log files and no exception
# should go missing

logger = Logger(origin="pyra.core.main")


def run():

    StateInterface.initialize()
    StateInterface.update({"automation_should_be_running": False})
    StateInterface.update({"vbdsd_indicates_good_conditions": False})
    _CONFIG = ConfigInterface.read()

    logger.info(f"started mainloop inside process with PID {os.getpid()}")

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

        if not _CONFIG["general"]["test_mode"]:
            # Start or stop VBDSD in a thread
            vbdsd_should_be_running = _CONFIG["measurement_triggers"]["consider_vbdsd"]
            if vbdsd_should_be_running and not vbdsd_thread.is_running():
                logger.info("Starting VBDSD Thread")
                vbdsd_thread.start()
            if not vbdsd_should_be_running and vbdsd_thread.is_running():
                logger.info("Stopping VBDSD Thread")
                vbdsd_thread.stop()
        else:
            logger.info("pyra-core in test mode")
            logger.debug("Skipping VBDSD_Thread in test mode")

        new_exception = None
        try:
            for module in _modules:
                module.run(_CONFIG)
        except Exception as e:
            new_exception = e

        try:
            new_current_exceptions = [*current_exceptions]

            if new_exception is not None:
                if type(new_exception).__name__ not in current_exceptions:
                    new_current_exceptions.append(type(new_exception).__name__)
                    ExceptionEmailClient.handle_occured_exception(
                        _CONFIG["error_email"], new_exception
                    )
                    logger.exception(new_exception)
            else:
                if len(current_exceptions) > 0:
                    new_current_exceptions = []
                    ExceptionEmailClient.handle_resolved_exception(
                        _CONFIG["error_email"]
                    )
                    logger.info(f"All exceptions have been resolved.")

            # if no errors until now
            current_exceptions = [*new_current_exceptions]
        except Exception as e:
            logger.exception(e)

        logger.info("Ending Iteration")

        # wait rest of loop time
        elapsed_time = time.time() - start_time
        time_to_wait = _CONFIG["general"]["seconds_per_core_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
