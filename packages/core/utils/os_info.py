import psutil
import datetime

# TODO: Refine comment quality

class EnergyError(Exception):
    pass


def check_cpu_usage()->list:
    """returns cpu_percent for all cores -> list [cpu1%, cpu2%,...]"""
    return psutil.cpu_percent(interval=1, percpu=True)


def ceck_average_system_load() ->list:
    """returns average system load in the last [1min,5min,15min] in %"""
    return [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]


def check_memory_usage()->float:
    """
    returns -> tuple (total, available, percent, used, free, active, inactive,
    buffers, cached, shared, slab)
    """
    v_memory = psutil.virtual_memory()
    return v_memory.percent


def check_disk_space()->float:
    """Returns disk space used in % as float.
    -> tuple (total, used, free, percent)"""
    disk = psutil.disk_usage('/')
    return disk.percent

#ip connections
def check_conecction_status(ip: str) -> str:
    """Checks the ip connection.
    Takes IP as input as str: i.e. 10.10.0.4
    and returns status i.e. ESTABLISHED
    """
    connections = psutil.net_connections(kind="inet4")

    for connection in connections:
        if connection.raddr:
            if connection.raddr[0] == ip:
                return connection.status


#battery
def check_system_battery():
    if psutil.sensors_battery().percent < 20:
        raise EnergyError("The battery of the system is below 20%.")


#time since last boot up
def time_since_os_boot():
    return datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")


#check process status
def check_process_status(process_name:str) -> str:
    """Takes a process name "*.exe" and returns its OS process status: i.e.
    "running".
    """
    for p in psutil.process_iter():
        if p.name() == process_name:
            return p.status()
