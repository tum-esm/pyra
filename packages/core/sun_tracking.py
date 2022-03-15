# CamTracker is a software that controls two electro motors that are connected
# to mirrors. It tracks the sun movement and allows the spectrometer to follow
# the sun in the course of the day.

# TODO: Implement this for the "Camtracker" software
# Later, make an abstract base class that enforces a standard interface
# to be implemented for any software like "Camtracker"

# TODO: Mock the behaviour of OPUS when testing


import logging
import pywin32

logger = logging.getLogger("pyra.core")


class SunTracking:
    @staticmethod
    def run():
        logger.info("Running SunTracking")
        pass

    def __start_sun_tracking_automation(self):
        #delete stop.txt file in camtracker folder if present
        #exe call with -automation
        camtracker_call = "c/:camtracker.exe -automation"
        hProcess, hThread, dwProcessId, dwThreadId = pywin32.CreateProcess(None, camtracker_call, None, None, 0,
                                                                           win32con.NORMAL_PRIORITY_CLASS, None,
                                                                           None, None)


    def __stop_sun_tracking_automation(self):
        #create stop.txt file in camtracker folder
        pass

    def __get_vbdsd_sun_status(self):
        #reads for outside sun conditions to start tracking
        #return
        pass

    def __get_camtracker_sun_status(self):
        #check sun status logged by camtracker
        pass

    def __get_camtracker_position(self):
        pass

    def __move_enclosure_cover(self):
        #move enclosure cover to sun positin
        pass

    def __read_motor_offsets(self):
        #read azimuth and elevation motor offsets from camtracker logfiles
        pass
