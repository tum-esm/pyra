import psutil
import tum_esm_utils


class OSInterface:
    @staticmethod
    class StorageError(Exception):
        """Raised when storage is more than 90% full"""

    @staticmethod
    class LowEnergyError(Exception):
        """Raised when battery is less than 20% full"""

    @staticmethod
    def validate_disk_space() -> None:
        """Raises a `OSInterface.StorageError` the disk is more than 90% full"""

        if tum_esm_utils.system.get_disk_space() > 90:
            raise OSInterface.StorageError(
                "Disk space is less than 10%. This is bad for the OS stability."
            )

    @staticmethod
    def validate_system_battery() -> None:
        """Raises LowEnergyError if system battery runs lower than 20%."""

        battery_level = tum_esm_utils.system.get_system_battery()
        if battery_level is not None:
            if battery_level < 20:
                raise OSInterface.LowEnergyError(
                    "The battery of the system is below 20%. Please check the power supply."
                )

    @staticmethod
    def get_process_status(process_name: str, ) -> str:
        """Takes a process name "*.exe" and returns its OS process
        status (see return types)."""

        for p in psutil.process_iter():
            if p.name() == process_name:
                return p.status()

        return "not-found"
