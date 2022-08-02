from packages.core.utils import Logger, OSInterface
from packages.core.utils.interfaces.state_interface import StateInterface

logger = Logger(origin="system-checks")


class SystemChecks:
    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config

    def run(self, new_config: dict):
        self._CONFIG = new_config
        logger.info("Running SystemChecks")

        # check os system stability
        cpu_usage = OSInterface.get_cpu_usage()
        logger.debug(f"Current CPU usage for all cores is {cpu_usage}%.")

        memory_usage = OSInterface.get_memory_usage()
        logger.debug(f"Current v_memory usage for the system is {memory_usage}.")

        last_boot_time = OSInterface.get_last_boot_time()
        logger.debug(f"The system is running since {last_boot_time}.")

        disk_space = OSInterface.get_disk_space()
        logger.debug(f"The disk is currently filled with {disk_space}%.")

        # raises error if disk_space is below 10%
        OSInterface.validate_disk_space()

        # raises error if system battery is below 20%
        OSInterface.validate_system_battery()

        StateInterface.update(
            {
                "os_state": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "last_boot_time": last_boot_time,
                    "filled_disk_space_fraction": disk_space,
                }
            }
        )
