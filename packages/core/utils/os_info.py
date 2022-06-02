import psutil
import datetime


class LowEnergyError(Exception):
    pass

class StorageError(Exception):
    pass

class OSInfo:
    @staticmethod
    def check_cpu_usage()->list:
        """returns cpu_percent for all cores -> list [cpu1%, cpu2%,...]"""
        return psutil.cpu_percent(interval=1, percpu=True)


    @staticmethod
    def check_average_system_load() ->list:
        """returns average system load in the last [1min,5min,15min] in %"""
        return [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]


    @staticmethod
    def check_memory_usage()->float:
        """returns -> tuple (total, available, percent, used, free, active, inactive,
        buffers, cached, shared, slab)
        """
        v_memory = psutil.virtual_memory()
        return v_memory.percent

    @staticmethod
    def check_disk_space()->float:
        """Returns disk space used in % as float.
        -> tuple (total, used, free, percent)"""
        disk = psutil.disk_usage('/')
        return disk.percent
    @staticmethod
    def validate_disk_space():
        """Raises an error if the diskspace is less than 10%"""
        if check_disk_space() < 10:
            raise StorageError

    @staticmethod
    def check_connection_status(ip: str) -> str:
        """Checks the ip connection.
        Takes IP as input as str: i.e. 10.10.0.4
        and returns status i.e. ESTABLISHED
        returns NOINFO if IP is not found.
        """
        connections = psutil.net_connections(kind="inet4")

        for connection in connections:
            if connection.raddr:
                if connection.raddr[0] == ip:
                    return connection.status
                else:
                    return "NOINFO"

    @staticmethod
    def check_system_battery()->float:
        """Returns system battery in percent as a float"""
        return psutil.sensors_battery().percent

    @staticmethod
    def validate_system_battery():
        """Raises LowEnergyError if system battery runs lower than 20%."""
        if check_system_battery() < 20.0:
            raise LowEnergyError("The battery of the system is below 20%.")

    @staticmethod
    def time_since_os_boot():
        """Returns time since last OS boot up."""
        return datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def check_process_status(process_name:str) -> str:
        """Takes a process name "*.exe" and returns its OS process status: i.e.
        "running".
        returns "not found" if process is not found.
        """
        for p in psutil.process_iter():
            if p.name() == process_name:
                return p.status()
            else:
                return "not found"
