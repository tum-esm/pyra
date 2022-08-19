from ctypes import Union
from typing import Literal
import psutil
import datetime


class OSInterface:
    @staticmethod
    class StorageError(Exception):
        """Raised when storage is more than 90% full"""

    @staticmethod
    class LowEnergyError(Exception):
        """Raised when battery is less than 20% full"""

    @staticmethod
    def get_cpu_usage() -> list[float]:
        """returns cpu_percent for all cores -> list [cpu1%, cpu2%,...]"""
        return psutil.cpu_percent(interval=1, percpu=True)  # type: ignore

    @staticmethod
    def get_memory_usage() -> float:
        """returns -> tuple (total, available, percent, used, free, active, inactive,
        buffers, cached, shared, slab)
        """
        v_memory = psutil.virtual_memory()
        return v_memory.percent

    @staticmethod
    def get_disk_space() -> float:
        """Returns disk space used in % as float.
        -> tuple (total, used, free, percent)"""
        disk = psutil.disk_usage("/")
        return disk.percent

    @staticmethod
    def validate_disk_space() -> None:
        """Raises an error if the diskspace is less than 10%"""
        if OSInterface.get_disk_space() > 90:
            raise OSInterface.StorageError(
                "Disk space is less than 10%. This is bad for the OS stability."
            )

    # TODO: function is not working as expected. Needs revision.
    @staticmethod
    def get_connection_status(
        ip: str,
    ) -> str:
        """
        Takes ip address as input str: i.e. 10.10.0.4
        Checks the ip connection for that address.
        """

        connections = psutil.net_connections(kind="inet4")

        for connection in connections:
            if connection.laddr:
                if connection.laddr.ip == ip:
                    return connection.status
            if connection.raddr:
                if connection.raddr.ip == ip:
                    return connection.status

        return "NO_INFO"

    @staticmethod
    def get_system_battery() -> int:
        """
        Returns system battery in percent as an integer (1-100).
        Returns 100 if device has no battery.
        """
        battery_state = psutil.sensors_battery()
        if battery_state is not None:
            return battery_state.percent
        return 100

    @staticmethod
    def validate_system_battery() -> None:
        """Raises LowEnergyError if system battery runs lower than 20%."""
        battery_state = psutil.sensors_battery()
        if battery_state is not None:
            if battery_state.percent < 20:
                raise OSInterface.LowEnergyError(
                    "The battery of the system is below 20%. Please check the power supply."
                )

    @staticmethod
    def get_last_boot_time() -> str:
        """Returns last OS boot time."""
        return datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def get_process_status(
        process_name: str,
    ) -> Literal[
        "running",
        "sleeping",
        "disk-sleep",
        "stopped",
        "tracing-stop",
        "zombie",
        "dead",
        "wake-kill",
        "waking",
        "idle",
        "locked",
        "waiting",
        "suspended",
        "parked",
        "not-found",
    ]:
        """
        Takes a process name "*.exe" and returns its OS process
        status (see return types).
        """
        for p in psutil.process_iter():
            if p.name() == process_name:
                return p.status()

        return "not-found"
