import threading
import time

import tum_esm_utils

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


class SystemMonitorThread(AbstractThread):
    """Thread for checking the system's state (CPU usage, disk utilization, etc.)"""

    logger_origin = "system-monitor-thread"

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=SystemMonitorThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="system-monitor", just_print=headless)
        logger.info("Starting System Monitor thread")
        activity_history_interface = interfaces.ActivityHistoryInterface(logger)

        while True:
            try:
                logger.debug("Starting iteration")

                # CPU/MEMORY USAGE AND BOOT TIME

                cpu_usage = tum_esm_utils.system.get_cpu_usage()
                logger.debug(
                    f"Current CPU usage for all cores is: {' | '.join([f'{int(u)} %' for u in cpu_usage])}."
                )

                memory_usage = tum_esm_utils.system.get_memory_usage()
                logger.debug(f"Current v_memory usage for the system is {memory_usage} %.")

                last_boot_time = tum_esm_utils.system.get_last_boot_time()
                logger.debug(f"The system is running since {last_boot_time}.")

                # DISK SPACE

                disk_space = tum_esm_utils.system.get_disk_space()
                logger.debug(f"The disk is currently filled with {disk_space} %.")
                if disk_space > 90:
                    subject = "StorageError"
                    details = "Disk space is more than 90%. This is bad for the OS stability."
                    with interfaces.StateInterface.update_state() as state:
                        state.exceptions_state.add_exception_state_item(
                            types.ExceptionStateItem(
                                origin="system-monitor", subject=subject, details=details
                            )
                        )
                    logger.error(f"{subject}: {details}")

                # BATTERY LEVEL

                battery_level = tum_esm_utils.system.get_system_battery()
                if battery_level is not None:
                    logger.debug(f"The battery level is {battery_level} %.")
                    if battery_level < 30:
                        subject = "LowEnergyError"
                        details = (
                            "The battery of the system is below 30%. Please check the power supply."
                        )
                        with interfaces.StateInterface.update_state() as state:
                            state.exceptions_state.add_exception_state_item(
                                types.ExceptionStateItem(
                                    origin="system-monitor", subject=subject, details=details
                                )
                            )
                        logger.error(f"{subject}: {details}")

                # UPDATE STATE AND FETCH RECENT ACTIVITY

                with interfaces.StateInterface.update_state() as state:
                    state.operating_system_state = types.OperatingSystemState(
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        last_boot_time=str(last_boot_time),
                        filled_disk_space_fraction=disk_space,
                    )
                    state.exceptions_state.clear_exception_origin("system-monitor")

                    is_measuring = state.measurements_should_be_running
                    has_errors = len(state.exceptions_state.current) > 0
                    new_camtracker_startups = state.activity.camtracker_startups
                    new_opus_startups = state.activity.opus_startups
                    new_cli_calls = state.activity.cli_calls
                    is_uploading = state.activity.upload_is_running

                    state.activity.camtracker_startups = 0
                    state.activity.opus_startups = 0
                    state.activity.cli_calls = 0

                # WRITE OUT UPDATED ACTIVITY HISTORY

                current_ah, current_ah_index = activity_history_interface.get()

                current_ah.core_is_running[current_ah_index] = 1
                current_ah.is_measuring[current_ah_index] = 1 if is_measuring else 0
                current_ah.has_errors[current_ah_index] = 1 if has_errors else 0
                current_ah.camtracker_startups[current_ah_index] += new_camtracker_startups
                current_ah.opus_startups[current_ah_index] += new_opus_startups
                current_ah.cli_calls[current_ah_index] += new_cli_calls
                current_ah.upload_is_running[current_ah_index] = 1 if is_uploading else 0

                activity_history_interface.update(current_ah)

                # SLEEP FOR 30 SECONDS

                logger.debug("Sleeping 30 seconds")
                time.sleep(30)

            except Exception as e:
                logger.exception(e)
                activity_history_interface.flush()
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.add_exception(origin="system-monitor", exception=e)
