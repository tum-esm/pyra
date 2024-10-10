import sys
import threading
import tum_esm_utils
from .abstract_thread import AbstractThread
from packages.core import interfaces, types, utils


class SystemChecksThread(AbstractThread):
    """Thread for checking the system's state (CPU usage, disk utilization, etc.)"""
    @staticmethod
    class StorageError(Exception):
        """Raised when storage is more than 90% full"""

    @staticmethod
    class LowEnergyError(Exception):
        """Raised when battery is less than 20% full"""

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=SystemChecksThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode, 
        don't write to log files but print to console."""

        logger = utils.Logger(origin="system-checks", just_print=headless)
        logger.info("Running SystemChecks")

        while True:
            try:
                # WINDOWS32 AND PYTHON VERSION >= 3.10

                if sys.platform != "win32":
                    subject = "UnsupportedPlatformError"
                    details = f"This function cannot be run on this platform ({sys.platform}). It requires 32-bit Windows."
                    logger.error(f"{subject}: {details}")
                    with interfaces.StateInterface.update_state() as state:
                        state.exceptions_state.add_exception_state_item(
                            types.ExceptionStateItem(
                                origin="system-checks", subject=subject, details=details
                            )
                        )

                if (sys.version_info.major != 3) or (sys.version_info.minor < 10):
                    subject = "UnsupportedPythonVersionError"
                    details = f"This function requires Python >= 3.10. Current version is {sys.version_info.major}.{sys.version_info.minor}."
                    logger.error(f"{subject}: {details}")
                    with interfaces.StateInterface.update_state() as state:
                        state.exceptions_state.add_exception_state_item(
                            types.ExceptionStateItem(
                                origin="system-checks", subject=subject, details=details
                            )
                        )

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
                                origin="system-checks", subject=subject, details=details
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
                                    origin="system-checks", subject=subject, details=details
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
                    state.exceptions_state.clear_exception_origin("system-checks")

                logger.info("Waiting 3 minutes before next system check")

            except Exception as e:
                logger.exception(e)
                with interfaces.StateInterface.update_state() as state:
                    state.exceptions_state.add_exception(origin="system-checks", exception=e)
