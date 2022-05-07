# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220421
# version           : 1.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# ==============================================================================

import snap7
import time
from packages.core.utils.json_file_interaction import State
from packages.core.utils.logger import Logger

logger = Logger(origin="pyra.core.enclosure-control")


class EnclosureControl:
    """
    https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
    """

    def __init__(self, initial_setup: dict, initial_parameters: dict):
        self._SETUP = initial_setup
        self._PARAMS = initial_parameters
        self.plc = snap7.client.Client()
        self.connection = self.plc_connect()
        self.last_cycle_automation_status = 0
        self.plc_write_bool(self._SETUP["plc"]["control"]["auto_temp_mode"], True)

    def run(self, new_setup: dict, new_parameters: dict):
        self._SETUP, self._PARAMS = new_setup, new_parameters

        logger.info("Running EnclosureControl")
        if not self._SETUP["enclosure"]["tum_enclosure_is_present"]:
            logger.debug("TUM enclosure not present. Skip Enclosure_Control.run().")
            return

        # check for automation state flank changes
        automation_should_be_running = State.read()["automation_should_be_running"]
        if self.last_cycle_automation_status != automation_should_be_running:
            if automation_should_be_running:
                # flank change 0 -> 1: load experiment, start macro
                self.plc_write_bool(self._SETUP["plc"]["control"]["sync_to_tracker"])
                logger.info("Syncing Cover to Tracker.")
            else:
                # flank change 1 -> 0: stop macro
                self.plc_write_bool(self._SETUP["plc"]["actors"]["move_cover"], 0)
                logger.info("Closing Cover.")

        # save the automation status for the next run
        self.last_cycle_automation_status = automation_should_be_running

        # TODO: Wait before checking again? Since the cover takes some time to move.
        if not automation_should_be_running:
            self.double_check_to_close_cover()

        # TODO: Trigger user warning if cover does not close?

        # read current state of actors and sensors in enclosure
        current_reading = self.read_state_from_plc()
        logger.info("New continuous readings.")
        State.update({"enclosure_plc_readings": current_reading})

        # possibly powerup/down spectrometer
        self.manage_spectrometer_power()

        # TODO: check what resetbutton after rain does (and the auto reset option

    def double_check_to_close_cover(self):
        """
        Triggers another close clover, if not yet closed and automation inactive.
        """
        if not self._PARAMS["plc"]["actors"]["cover_closed"]:
            self.plc_write_bool(self._SETUP["plc"]["actors"]["move_cover"], 0)
            logger.info("Cover is still open. Trying to close again.")

    def manage_spectrometer_power(self):
        """
        Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """

        current_sun_elevation = State.read()["current_sun_elevation"]
        min_sun_angle = self._PARAMS["enclosure"]["min_sun_angle"]
        spectrometer_has_power = self.plc_read_bool(
            self._SETUP["plc"]["power"]["spectrometer"]
        )

        if current_sun_elevation is not None:
            if (current_sun_elevation > min_sun_angle) and (not spectrometer_has_power):
                self.plc_write_bool(self._SETUP["plc"]["power"]["spectrometer"], True)
                logger.info("Powering up the spectrometer.")
            elif spectrometer_has_power:
                self.plc_write_bool(self._SETUP["plc"]["power"]["spectrometer"], False)
                logger.info("Powering down the spectrometer.")

    def read_state_from_plc(self):
        """
        Checks the state of the enclosure by continuously reading sensor and
        actor output.

        returns
        r: list
        """
        return [
            self.plc_read_int(self._SETUP["plc"]["actors"]["fan_speed"]),
            self.plc_read_int(self._SETUP["plc"]["actors"]["current_angle"]),
            self.plc_read_bool(self._SETUP["plc"]["control"]["auto_temp_mode"]),
            self.plc_read_bool(self._SETUP["plc"]["control"]["manual_control"]),
            self.plc_read_bool(self._SETUP["plc"]["control"]["manual_temp_mode"]),
            self.plc_read_int(self._SETUP["plc"]["sensors"]["humidity"]),
            self.plc_read_int(self._SETUP["plc"]["sensors"]["temperature"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["camera"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["computer"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["cover"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["heater"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["motor_failed"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["rain"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["reset_needed"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["router"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["spectrometer"]),
            self.plc_read_bool(self._SETUP["plc"]["state"]["ups_alert"]),
        ]

    def plc_connect(self):
        """
        Connects to the PLC Snap7

        Returns:
        True -> connected
        False -> not connected
        """
        self.plc.connect("10.10.0.4", 0, 1)
        return self.plc.get_connected()

    def plc_disconnect(self):
        """
        Disconnects from the PLC Snap7

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
        """
        Connects to the PLC Snap7

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
