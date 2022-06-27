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
import os
import astropy.units as astropy_units
from packages.core.utils import (
    StateInterface,
    Logger,
    Astronomy,
    STANDARD_PLC_INTERFACES,
    PLCInterface,
    with_timeout,
)

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
        if self._CONFIG["general"]["test_mode"]:
            return

        if self._CONFIG["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        self._PLC_INTERFACE: PLCInterface = STANDARD_PLC_INTERFACES[
            self._CONFIG["tum_plc"]["version"]
        ]

        self.plc = snap7.client.Client()
        self.connection = self.plc_connect()
        self.last_cycle_automation_status = 0
        self.set_auto_temperature(True)

    def run(self, new_config: dict):
        self._CONFIG = new_config
        if self._CONFIG["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        if self._CONFIG["general"]["test_mode"]:
            logger.debug("Skipping EnclosureControl in test mode")
            return
        if self._CONFIG["tum_plc"]["controlled_by_user"]:
            logger.debug("Skipping EnclosureControl because enclosure is controlled by user")
            return

        self._PLC_INTERFACE: PLCInterface = STANDARD_PLC_INTERFACES[
            self._CONFIG["tum_plc"]["version"]
        ]
        logger.info("Running EnclosureControl")

        # check PLC ip connection
        if self.is_PLC_responsive():
            logger.debug("Successful ping to PLC.")
        else:
            raise PLCError("Could not find an active PLC IP connection.")

        # check for automation state flank changes
        automation_should_be_running = StateInterface.read()["automation_should_be_running"]
        if self.last_cycle_automation_status != automation_should_be_running:
            if automation_should_be_running:
                # flank change 0 -> 1: load experiment, start macro
                if self.check_for_reset_needed():
                    self.reset()
                    time.sleep(10)

                # TODO: add a check of the rain sensor before opening the cover

                self.set_sync_to_tracker(True)
                logger.info("Syncing Cover to Tracker.")
            else:
                # flank change 1 -> 0: stop macro
                self.set_sync_to_tracker(False)
                self.move_cover(0)
                logger.info("Closing Cover.")
                self.wait_for_cover_closing()

        # save the automation status for the next run
        self.last_cycle_automation_status = automation_should_be_running

        if not automation_should_be_running:
            if not self.check_cover_closed():
                logger.info("Cover is still open. Trying to close again.")
                self.move_cover(0)
                self.wait_for_cover_closing()

        # read current state of actors and sensors in enclosure
        current_reading = self.read_states_from_plc()
        logger.info("New continuous readings.")
        StateInterface.update({"enclosure_plc_readings": current_reading})

        # possibly powerup/down spectrometer
        self.auto_set_power_spectrometer()

    @with_timeout(3)
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

    def cpu_busy_check(self):
        """Wait until CPU is not busy anymore."""
        time.sleep(0.2)
        if str(self.plc.get_cpu_state()) == "S7CpuStatusRun":
            time.sleep(1)

    def plc_read_int(self, action):
        """Reads an INT value in the PLC database."""
        assert len(action) == 3
        db_number, start, size = action
        print(f"reading int: action={action}")

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
        print(f"reading bool: action={action}")

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

    # PLC.CONTROL SETTERS

    def set_sync_to_tracker(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.control.sync_to_tracker, state)

    def set_manual_control(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.control.manual_control, state)

    def set_auto_temperature(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.control.auto_temp_mode, state)

    def set_manual_temperature(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.control.manual_temp_mode, state)

    def reset(self):
        self.plc_write_bool(self._PLC_INTERFACE.control.reset, False)

    # PLC.POWER SETTERS

    def set_power_camera(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.power.camera, state)

    def set_power_computer(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.power.computer, state)

    def set_power_heater(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.power.heater, state)

    def set_power_router(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.power.router, state)

    def set_power_spectrometer(self, state=True):
        self.plc_write_bool(self._PLC_INTERFACE.power.spectrometer, state)

    # PLC.ACTORS SETTERS

    def move_cover(self, value: int):
        self.set_manual_control(True)
        self.plc_write_int(self._PLC_INTERFACE.actors.move_cover, value)
        self.set_manual_control(False)

    def force_cover_close(self):
        if self.check_for_reset_needed():
            self.reset()

        self.set_sync_to_tracker(False)
        self.set_manual_control(True)
        self.move_cover(0)
        self.wait_for_cover_closing()
        self.set_manual_control(True)

    def wait_for_cover_closing(self):
        """Waits steps of 5s for the enclosure cover to close.

        Raises the custom error CoverError if clover doesn't close in a given
        period of time.
        """

        start_time = time.time()
        loop = True

        while loop:
            time.sleep(5)

            if self.check_cover_closed():
                loop = False

            elapsed_time = time.time() - start_time
            if elapsed_time > 31:
                raise CoverError("Enclosure cover might be stuck.")

    # PLC GETTERS

    def check_cover_closed(self):
        return self.plc_read_bool(self._PLC_INTERFACE.state.cover_closed)

    def check_for_reset_needed(self):
        return self.plc_read_bool(self._PLC_INTERFACE.state.reset_needed)

    def read_states_from_plc(self) -> dict:
        """
        Checks the state of the enclosure by continuously reading sensor and
        actor output.
        """

        plc_db_content = {}
        plc_db_content[8] = self.plc.db_read(8, 0, 25)
        self.cpu_busy_check()
        plc_db_content[25] = self.plc.db_read(25, 0, 9)
        self.cpu_busy_check()
        plc_db_content[3] = self.plc.db_read(3, 0, 5)
        self.cpu_busy_check()

        def _get_int(spec: list[int]):
            return snap7.util.get_int(plc_db_content[spec[0]], spec[1])

        def _get_bool(spec: list[int]):
            return snap7.util.get_bool(plc_db_content[spec[0]], spec[1], spec[3])

        return {
            "actors": {
                "fan_speed": _get_int(self._PLC_INTERFACE.actors.fan_speed),
                "current_angle": _get_int(self._PLC_INTERFACE.actors.current_angle),
            },
            "control": {
                "auto_temp_mode": _get_bool(self._PLC_INTERFACE.control.auto_temp_mode),
                "manual_control": _get_bool(self._PLC_INTERFACE.control.manual_control),
                "manual_temp_mode": _get_bool(self._PLC_INTERFACE.control.manual_temp_mode),
                "sync_to_tracker": _get_bool(self._PLC_INTERFACE.control.sync_to_tracker),
            },
            "sensors": {
                "humidity": _get_int(self._PLC_INTERFACE.sensors.humidity),
                "temperature": _get_int(self._PLC_INTERFACE.sensors.temperature),
            },
            "state": {
                "cover_closed": _get_bool(self._PLC_INTERFACE.state.cover_closed),
                "motor_failed": _get_bool(self._PLC_INTERFACE.state.motor_failed),
                "rain": _get_bool(self._PLC_INTERFACE.state.rain),
                "reset_needed": _get_bool(self._PLC_INTERFACE.state.reset_needed),
                "ups_alert": _get_bool(self._PLC_INTERFACE.state.ups_alert),
            },
            "power": {
                "camera": _get_bool(self._PLC_INTERFACE.power.camera),
                "computer": _get_bool(self._PLC_INTERFACE.power.computer),
                "heater": _get_bool(self._PLC_INTERFACE.power.heater),
                "router": _get_bool(self._PLC_INTERFACE.power.router),
                "spectrometer": _get_bool(self._PLC_INTERFACE.power.spectrometer),
            },
            "connections": {
                "camera": _get_bool(self._PLC_INTERFACE.connections.camera),
                "computer": _get_bool(self._PLC_INTERFACE.connections.computer),
                "heater": _get_bool(self._PLC_INTERFACE.connections.heater),
                "router": _get_bool(self._PLC_INTERFACE.connections.router),
                "spectrometer": _get_bool(self._PLC_INTERFACE.connections.spectrometer),
            },
        }

    # -------------------------------------------------------------------------

    def auto_set_power_spectrometer(self):
        """
        Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """

        current_sun_elevation = Astronomy.get_current_sun_elevation()
        min_power_elevation = (
            self._CONFIG["tum_plc"]["min_power_elevation"] * astropy_units.deg
        )
        spectrometer_has_power = self.read_power_spectrometer()

        print(current_sun_elevation > min_power_elevation)

        if current_sun_elevation is not None:
            if (current_sun_elevation >= min_power_elevation) and (not spectrometer_has_power):
                self.set_power_spectrometer(True)
                logger.info("Powering up the spectrometer.")
            elif (current_sun_elevation < min_power_elevation) and (spectrometer_has_power):
                self.set_power_spectrometer(False)
                logger.info("Powering down the spectrometer.")

    def is_PLC_responsive(self):
        """Pings the PLC and returns:

        True -> Connected
        False -> Not Connected"""
        response = os.system("ping -n 1 " + self._CONFIG["tum_plc"]["ip"])

        if response == 0:
            return True
        else:
            return False
