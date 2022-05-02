# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220401
# version           : 3.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# ==============================================================================

import json
import os
from filelock import FileLock
import snap7
import time

from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.enclosure-control")

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
SETUP_FILE_PATH = f"{PROJECT_DIR}/config/setup.json"
PARAMS_FILE_PATH = f"{PROJECT_DIR}/config/parameters.json"
CONFIG_LOCK_PATH = f"{PROJECT_DIR}/config/config.lock"


class EnclosureControl:
    """https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf"""

    def __init__(self):
        self._SETUP = {}
        self._PARAMS = {}
        self.plc = snap7.client.Client()
        self.connection = self.plc_connect()
        self.last_cycle_automation_status = 0
        self.plc_write_bool(self._SETUP["plc"]["control"]["auto_temp_mode"])

    def run(self):
        logger.info("Running EnclosureControl")
        if not self._SETUP["enclosure"]["tum_enclosure_is_present"]:
            return

        # check for automation state flank changes
        if (
            self.last_cycle_automation_status
            != self._PARAMS["pyra"]["automation_status"]
        ):
            if self._PARAMS["pyra"]["automation_status"] == 1:
                # flank change 0 -> 1: load experiment, start macro
                self.plc_write_bool(self._SETUP["plc"]["control"]["sync_to_tracker"])

            if self._PARAMS["pyra"]["automation_status"] == 0:
                # flank change 1 -> 0: stop macro
                self.plc_write_bool(self._SETUP["plc"]["actors"]["move_cover"], 0)

        # save the automation status for the next run
        self.last_cycle_automation_status = self._PARAMS["pyra"]["automation_status"]

        # double check that cover is closed if automation == 0
        self.double_check_cover()
        # TODO: Trigger user warning?

        # read current state of actors and sensors in enclosure
        current_reading = self.continuous_readings()

        with FileLock(CONFIG_LOCK_PATH):
            with open(PARAMS_FILE_PATH, "w") as f:
                self._PARAMS["enclosure"]["continuous_readings"] = current_reading
                json.dump(self._PARAMS, f, indent=2)

        # powerup spectrometer if sun angle is 10° or more
        self.manage_spectrometer_power()

        # TODO: check what resetbutton after rain does (and the auto reset option

    @property
    def set_config(self):
        pass

    @set_config.setter
    def set_config(self, vals):
        self._SETUP, self._PARAMS = vals

    def double_check_cover(self):
        """Triggers another close clover, if not yet closed and automation
        inactive.
        """
        if self._PARAMS["pyra"]["automation_status"] == 0:
            if not self._PARAMS["plc"]["actors"]["cover_closed"]:
                self.plc_write_bool(self._SETUP["plc"]["actors"]["move_cover"], 0)

    def manage_spectrometer_power(self):
        """Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """
        if (
            self.plc_read_bool(
                self._PARAMS["measurement_conditions"]["current_sun_angle"]
            )
            > self._PARAMS["enclsoure"]["min_sun_angle"]
        ):
            if not self.plc_read_bool(self._SETUP["plc"]["power"]["spectrometer"]):
                self.plc_write_bool(self._SETUP["plc"]["power"]["spectrometer"], True)

        if (
            self.plc_read_bool(
                self._PARAMS["measurement_conditions"]["current_sun_angle"]
            )
            < self._PARAMS["enclsoure"]["min_sun_angle"]
        ):
            if self.plc_read_bool(self._SETUP["plc"]["power"]["spectrometer"]):
                self.plc_write_bool(self._SETUP["plc"]["power"]["spectrometer"], False)

    def continuous_readings(self):
        """Checks the state of the enclosure by continuously reading sensor and
        actor output.

        returns
        r: list
        """
        r = []

        # actors
        r.append(self.plc_read_bool(self._SETUP["plc"]["actors"]["cover_closed"]))
        r.append(self.plc_read_int(self._SETUP["plc"]["actors"]["fan_speed"]))
        r.append(self.plc_read_int(self._SETUP["plc"]["actors"]["current_angle"]))
        # control
        r.append(self.plc_read_bool(self._SETUP["plc"]["control"]["auto_temp_mode"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["control"]["manual_control"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["control"]["manual_temp_mode"]))
        # sensors
        r.append(self.plc_read_int(self._SETUP["plc"]["sensors"]["humidity"]))
        r.append(self.plc_read_int(self._SETUP["plc"]["sensors"]["temperature"]))
        # state
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["camera"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["computer"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["cover"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["heater"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["motor_failed"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["rain"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["reset_needed"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["router"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["spectrometer"]))
        r.append(self.plc_read_bool(self._SETUP["plc"]["state"]["ups_alert"]))

        return r

    def plc_connect(self):
        """Connects to the PLC Snap7

        Returns:
        True -> connected
        False -> not connected
        """
        self.plc.connect("10.10.0.4", 0, 1)
        return self.plc.get_connected()

    def plc_disconnect(self):
        """Disconnects from the PLC Snap7

        Returns:
        True -> disconnected
        False -> not disconnected
        """
        self.plc.disconnect()

        if not self.plc.get_connected():
            return True
        else:
            return False

    def plc_connected(self):
        """Connects to the PLC Snap7

        Returns:
        True -> connected
        False -> not connected
        """
        return self.plc.get_connected()

    def plc_read_int(self, action):
        """Redas an INT value in the PLC database."""
        assert len(action) == 3
        db_number, start, size = action

        msg = self.plc.db_read(db_number, start, size)
        value = snap7.util.get_int(msg, 0)

        # wait if cpu is still busy
        self.cpu_busy_check()

        return value

    def plc_write_int(self, action, value):
        """Changes an INT value in the PLC database."""
        assert len(action) == 3
        db_number, start, size = action

        msg = bytearray(size)
        snap7.util.set_int(msg, 0, value)
        self.plc.db_write(db_number, start, msg)

        # wait if cpu is still busy
        self.cpu_busy_check()

    def plc_read_bool(self, action):
        """Reads a BOOL value in the PLC database."""
        assert len(action) == 4
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        value = snap7.util.get_bool(msg, 0, bool_index)

        # wait if cpu is still busy
        self.cpu_busy_check()

        return value

    def plc_write_bool(self, action, value):
        """Changes a BOOL value in the PLC database."""
        assert len(action) == 4
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        snap7.util.set_bool(msg, 0, bool_index, value)
        self.plc.db_write(db_number, start, msg)

        # wait if cpu is still busy
        self.cpu_busy_check()

    def cpu_busy_check(self):
        """Sleeps if cpu is busy."""
        if str(self.plc.get_cpu_state()) == "S7CpuStatusRun":
            time.sleep(2)
