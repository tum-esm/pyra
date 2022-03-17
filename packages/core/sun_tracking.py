# CamTracker is a software that controls two electro motors that are connected
# to mirrors. It tracks the sun movement and allows the spectrometer to follow
# the sun in the course of the day.

# TODO: Implement this for the "Camtracker" software
# Later, make an abstract base class that enforces a standard interface
# to be implemented for any software like "Camtracker"

# TODO:


import logging
import pywin32
import os

logger = logging.getLogger("pyra.core")


class SunTracking:

    def __init__(self):
        self._PARAMS = {}
        self._SETUP = {}
        self.camtracker_process = (None, None, None, None)
        self.camtracker_application_status = 0


    def run(self, setup: dict, params: dict):
        logger.info("Running SunTracking")
        self.__update_json_config(setup, params)

        #check for PYRA Test Mode status
        if self._PARAMS["PYRA_test_mode"] == 1:
            return


        #startup camtrackerr automation: startup conditions given and inactive
        #stop camtracker automation: stop conditions given and active

        pass

    def __update_json_config(self, setup: dict, params: dict):
        """Updates class internal dictionaries to the latest version of the
        json files for SETUP and PARAMETERS.
        """
        self._SETUP = setup
        self._PARAMS = params

    def __update_camtracker_application_status(self):
        """Updates the parameter self.camtracker_application_status.
        Uses win32process from pywin32 module to check hProcess available
        in self.camtracker_process.

        0 if Application is currently not running on OS
        1 if Application is currently running on OS
        """
        # TODO: implement functionality
        pass

    def __start_sun_tracking_automation(self):
        """Uses win32process frm pywin32 module to start up the CamTracker
         executable with additional paramter -automation.
        The paramter - automation will instruct CamTracker to automatically
        move the mirrors to the expected sun position during startup.

         Returns pywin32 process information for later usage."""
        #delete stop.txt file in camtracker folder if present
        #exe call with -automation
        # http://timgolden.me.uk/pywin32-docs/win32process.html
        camtracker_call = self._PARAMS["CamTracker_executable_full_path"] \
                          + " -automation"
        hProcess, hThread, dwProcessId, dwThreadId = pywin32.CreateProcess(
            None,
            camtracker_call,
            None,
            None,
            0,
            win32con.NORMAL_PRIORITY_CLASS,
            None,
            None,
            None)

        return (hProcess, hThread, dwProcessId, dwThreadId)

    def __stop_sun_tracking_automation(self):
        """Tells the CamTracker application to end program and move mirrors
        to parking position.

        CamTracker has an internal check for a stop.txt file in its directory
        and will do a clean shutdown.
        """

        #create stop.txt file in camtracker folder
        camtracker_directory = os.path.dirname(
            self._PARAMS["CamTracker_executable_full_path"])
        f = open(camtracker_directory + "stop.txt", 'w')
        f.close()

    def __read_motor_offsets(self):
        # read azimuth and elevation motor offsets from camtracker logfiles
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


