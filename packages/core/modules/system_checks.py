# ==============================================================================
# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220421
# version           : 1.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# Measurement conditions checks for start and stop conditions that are set in
# the parameters json file. It can check for environmental conditions like sun
# status, temporal conditions like current time, or manual user input.
# ==============================================================================

from packages.core.utils import Logger, OSInterface

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

        average_system_load = OSInterface.get_average_system_load()
        logger.info(
            "The average system load in the past 1/5/15 "
            + f"minutes was {average_system_load}."
        )

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

        # TODO: Write system state into state.json
