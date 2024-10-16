import tum_esm_utils
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="system-checks")


class SystemChecks:
    """SystemChecks interacts with the present Operating System through
    `OSInterface`. It checks and logs important parameters (CPU, memory,
    disk space) to give insight into the overall system stability. It
    raises custom errors when the disk runs out of storage or the energy
    supply is not ensured. SystemChecks writes the latest readout into
    StateInterface."""
    def __init__(self, initial_config: types.Config):
        self.config = initial_config

    def run(self, new_config: types.Config) -> None:
        self.config = new_config
        logger.info("Running SystemChecks")

        # check os system stability
        cpu_usage = tum_esm_utils.system.get_cpu_usage()
        logger.debug(f"Current CPU usage for all cores is {cpu_usage}%.")

        memory_usage = tum_esm_utils.system.get_memory_usage()
        logger.debug(
            f"Current v_memory usage for the system is {memory_usage}."
        )

        last_boot_time = tum_esm_utils.system.get_last_boot_time()
        logger.debug(f"The system is running since {last_boot_time}.")

        disk_space = tum_esm_utils.system.get_disk_space()
        logger.debug(f"The disk is currently filled with {disk_space}%.")

        # raises error if disk_space is below 10%
        interfaces.OSInterface.validate_disk_space()

        # raises error if system battery is below 20%
        interfaces.OSInterface.validate_system_battery()

        interfaces.StateInterface.update_state(
            operating_system_state=types.OperatingSystemState(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                last_boot_time=str(last_boot_time),
                filled_disk_space_fraction=disk_space,
            )
        )
