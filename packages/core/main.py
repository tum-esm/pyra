import os
import time
from packages.core import modules
from packages.core.utils import (
    ConfigInterface,
    StateInterface,
    Logger,
    ExceptionEmailClient,
)

logger = Logger(origin="main")


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
    vbdsd_thread = modules.vbdsd.VBDSD_Thread()

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

        if not _CONFIG["general"]["test_mode"]:
            # Start or stop VBDSD in a thread
            vbdsd_should_be_running = (
                _CONFIG["vbdsd"] is not None
                and _CONFIG["measurement_triggers"]["consider_vbdsd"]
            )
            if vbdsd_should_be_running and not vbdsd_thread.is_running():
                vbdsd_thread.start()
            if not vbdsd_should_be_running and vbdsd_thread.is_running():
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
            logger.exception(new_exception)

        try:
            new_current_exceptions = [*current_exceptions]

            if new_exception is not None:
                if type(new_exception).__name__ not in current_exceptions:
                    new_current_exceptions.append(type(new_exception).__name__)
                    ExceptionEmailClient.handle_occured_exception(_CONFIG, new_exception)
                    if len(current_exceptions) == 0:
                        Logger.log_activity_event("error-occured")
            else:
                if len(current_exceptions) > 0:
                    new_current_exceptions = []
                    ExceptionEmailClient.handle_resolved_exception(_CONFIG)
                    logger.info(f"All exceptions have been resolved.")
                    Logger.log_activity_event("errors-resolved")

            # if no errors until now
            current_exceptions = [*new_current_exceptions]
            StateInterface.update({"current_exceptions": current_exceptions}, persistent=True)
        except Exception as e:
            logger.exception(e)

        logger.info("Ending iteration")

        # wait rest of loop time
        elapsed_time = time.time() - start_time
        time_to_wait = _CONFIG["general"]["seconds_per_core_interval"] - elapsed_time
        if time_to_wait > 0:
            logger.debug(f"Waiting {round(time_to_wait, 2)} second(s)")
            time.sleep(time_to_wait)
