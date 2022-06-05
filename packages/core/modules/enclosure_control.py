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
from packages.core.utils import StateInterface, Logger, OSInfo, Astronomy

logger = Logger(origin="pyra.core.enclosure-control")


class CoverError(Exception):
    pass


class PLCError(Exception):
    pass


class EnclosureControl:
    """
    https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
    """

    def __init__(self, initial_config: dict):
        self._CONFIG = initial_config
        if self._CONFIG["tum_plc"] is None:
            logger.debug("TUM PLC is not present. Skipping Enclosure_Control.__init__")
            return

        self.plc = snap7.client.Client()
        self.connection = self.plc_connect()
        self.last_cycle_automation_status = 0
        self.plc_write_bool(self._CONFIG["tum_plc"]["control"]["auto_temp_mode"], True)

    def run(self, new_config: dict):
        self._CONFIG = new_config
        logger.info("Running EnclosureControl")
        if self._CONFIG["tum_plc"] is None:
            logger.debug("TUM PLC is not present. Skipping Enclosure_Control.run")
            return

        # check PLC ip connection
        plc_status = OSInfo.check_connection_status(self._CONFIG["tum_plc"]["ip"])
        logger.debug("The PLC IP connection returned the status {}.".format(plc_status))

        if plc_status == "NO_INFO":
            raise PLCError("Could not find an active PLC IP connection.")

        # check for automation state flank changes
        automation_should_be_running = StateInterface.read()[
            "automation_should_be_running"
        ]
        if self.last_cycle_automation_status != automation_should_be_running:
            if automation_should_be_running:
                # flank change 0 -> 1: load experiment, start macro
                # TODO: check if that is correct reset handling
                if self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["reset_needed"]):
                    self.plc_write_bool(
                        self._CONFIG["tum_plc"]["control"]["reset"], False
                    )
                    time.sleep(10)

                self.plc_write_bool(
                    self._CONFIG["tum_plc"]["control"]["sync_to_tracker"], True
                )
                logger.info("Syncing Cover to Tracker.")
            else:
                # flank change 1 -> 0: stop macro
                self.plc_write_bool(
                    self._CONFIG["tum_plc"]["control"]["sync_to_tracker"], False
                )
                self.plc_write_int(self._CONFIG["tum_plc"]["actors"]["move_cover"], 0)
                logger.info("Closing Cover.")
                self.wait_for_cover_closing()

        # save the automation status for the next run
        self.last_cycle_automation_status = automation_should_be_running

        if not automation_should_be_running:
            if not self._CONFIG["tum_plc"]["actors"]["cover_closed"]:
                logger.info("Cover is still open. Trying to close again.")
                self.plc_write_int(self._CONFIG["tum_plc"]["actors"]["move_cover"], 0)
                self.wait_for_cover_closing()

        # read current state of actors and sensors in enclosure
        current_reading = self.read_state_from_plc()
        logger.info("New continuous readings.")
        StateInterface.update({"enclosure_plc_readings": current_reading})

        # possibly powerup/down spectrometer
        self.manage_spectrometer_power()

        # TODO: check what resetbutton after rain does (and the auto reset option

    def manage_spectrometer_power(self):
        """
        Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """

        current_sun_elevation = Astronomy.get_current_sun_elevation()
        min_power_elevation = self._CONFIG["tum_plc"]["min_power_elevation"]
        spectrometer_has_power = self.plc_read_bool(
            self._CONFIG["tum_plc"]["power"]["spectrometer"]
        )

        if current_sun_elevation is not None:
            if (current_sun_elevation > min_power_elevation) and (
                not spectrometer_has_power
            ):
                self.plc_write_bool(
                    self._CONFIG["tum_plc"]["power"]["spectrometer"], True
                )
                logger.info("Powering up the spectrometer.")
            elif spectrometer_has_power:
                self.plc_write_bool(
                    self._CONFIG["tum_plc"]["power"]["spectrometer"], False
                )
                logger.info("Powering down the spectrometer.")

    def read_state_from_plc(self):
        """
        Checks the state of the enclosure by continuously reading sensor and
        actor output.

        returns
        r: list
        """
        return [
            self.plc_read_int(self._CONFIG["tum_plc"]["actors"]["fan_speed"]),
            self.plc_read_int(self._CONFIG["tum_plc"]["actors"]["current_angle"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["control"]["auto_temp_mode"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["control"]["manual_control"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["control"]["manual_temp_mode"]),
            self.plc_read_int(self._CONFIG["tum_plc"]["sensors"]["humidity"]),
            self.plc_read_int(self._CONFIG["tum_plc"]["sensors"]["temperature"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["camera"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["computer"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["cover_closed"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["heater"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["motor_failed"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["rain"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["reset_needed"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["router"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["spectrometer"]),
            self.plc_read_bool(self._CONFIG["tum_plc"]["state"]["ups_alert"]),
        ]

    def plc_connect(self):
        """
        Connects to the PLC Snap7

        Returns:
        True -> connected
        False -> not connected
        """
        self.plc.connect(self._CONFIG["tum_plc"]["ip"], 0, 1)
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
        """Reads an INT value in the PLC database."""
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

    def wait_for_cover_closing(self):
        """Waits steps of 5s for the enclosure cover to close.

        Raises the custom error CoverError if clover doesn't close in a given
        period of time.
        """

        start_time = time.time()
        loop = True

        while loop:
            time.sleep(5)

            if self.plc_read_bool(["tum_plc"]["state"]["cover_closed"]):
                loop = False

            elapsed_time = time.time() - start_time
            if elapsed_time > 31:
                raise CoverError("Enclosure cover might be stuck.")
