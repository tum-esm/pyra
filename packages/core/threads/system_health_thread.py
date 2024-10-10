import threading
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils

ORIGIN = "system-health"


class SystemHealthThread(AbstractThread):
    """Thread for checking the system's state (CPU usage, disk utilization, etc.)"""
    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=SystemHealthThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        logger = utils.Logger(origin=ORIGIN, just_print=headless)

        while True:
            try:
                logger.info("Running system health checks")

                # CPU/MEMORY USAGE AND BOOT TIME

                cpu_usage = tum_esm_utils.system.get_cpu_usage()
                logger.debug(f"Current CPU usage for all cores is {cpu_usage}%.")

                memory_usage = tum_esm_utils.system.get_memory_usage()
                logger.debug(f"Current v_memory usage for the system is {memory_usage}.")

                last_boot_time = tum_esm_utils.system.get_last_boot_time()
                logger.debug(f"The system is running since {last_boot_time}.")

                # DISK SPACE

                disk_space = tum_esm_utils.system.get_disk_space()
                logger.debug(f"The disk is currently filled with {disk_space}%.")
                if disk_space > 90:
                    subject = "StorageError"
                    details = "Disk space is more than 90%. This is bad for the OS stability."
                    with interfaces.StateInterface.update_state() as state:
                        state.exceptions_state.add_exception_state_item(
                            types.ExceptionStateItem(
                                origin=ORIGIN, subject=subject, details=details
                            )
                        )
                    logger.error(f"{subject}: {details}")

                # BATTERY LEVEL

                battery_level = tum_esm_utils.system.get_system_battery()
                logger.debug(f"The battery level is {battery_level}%.")
                if battery_level is not None:
                    if battery_level < 30:
                        subject = "LowEnergyError"
                        details = "The battery of the system is below 30%. Please check the power supply."
                        with interfaces.StateInterface.update_state() as state:
                            state.exceptions_state.add_exception_state_item(
                                types.ExceptionStateItem(
                                    origin=ORIGIN, subject=subject, details=details
                                )
                            )
                        logger.error(f"{subject}: {details}")

                with interfaces.StateInterface.update_state() as state:
                    state.operating_system_state = types.OperatingSystemState(
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        last_boot_time=str(last_boot_time),
                        filled_disk_space_fraction=disk_space,
                    )
                    state.exceptions_state.clear_exception_origin(ORIGIN)

                logger.info("Waiting 3 minutes before next check")

            except Exception as e:
                logger.exception(e)
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.add_exception(origin=ORIGIN, exception=e)
