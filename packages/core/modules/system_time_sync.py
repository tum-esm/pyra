# BktTimeSync is a software by IZ2BKT that synchronizes the system time with
# either a NTP Server or a GPS receiver. This is important to keep the time
# stamps accurate during the measurement.

# TODO: Implement this for the "BktTimeSync" software

# Later, make an abstract base class that enforces a standard interface
# to be implemented for any software like "BktTimeSync"

from packages.core.utils.logger import Logger


class SystemTimeSync:
    @staticmethod
    def run():
        Logger.info("Running SystemTimeSync")
        pass
