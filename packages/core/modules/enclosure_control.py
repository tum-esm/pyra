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

import time
import astropy.units as astropy_units
from packages.core.utils import StateInterface, Logger, Astronomy, PLCError, PLCInterface

logger = Logger(origin="pyra.core.enclosure-control")


class CoverError(Exception):
    pass


class EnclosureControl:
    """
    https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
    """

    def __init__(self, initial_config: dict):
        self.config = initial_config
        if self.config["general"]["test_mode"]:
            return

        if self.config["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        self.plc_interface = PLCInterface(self.config)
        self.plc_interface.set_auto_temperature(True)
        self.last_cycle_automation_status = 0

        # This state is read once per mainloop
        self.plc_state = self.plc_interface.read()

    def run(self, new_config: dict):
        self.config = new_config
        if self.config["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        if self.config["general"]["test_mode"]:
            logger.debug("Skipping EnclosureControl in test mode")
            return
        if self.config["tum_plc"]["controlled_by_user"]:
            logger.debug("Skipping EnclosureControl because enclosure is controlled by user")
            return

        logger.info("Running EnclosureControl")

        self.plc_interface.update_config(self.config)
        self.plc_state = self.plc_interface.read()

        # check PLC ip connection
        if self.plc_interface.is_responsive():
            logger.debug("Successful ping to PLC.")
        else:
            raise PLCError("Could not find an active PLC IP connection.")

        # check for automation state flank changes
        automation_should_be_running = StateInterface.read()["automation_should_be_running"]
        if self.last_cycle_automation_status != automation_should_be_running:
            if automation_should_be_running:
                # flank change 0 -> 1: load experiment, start macro
                if self.plc_state.state.reset_needed:
                    self.plc_interface.reset()
                    time.sleep(10)
                if not self.plc_state.state.rain:
                    self.plc_interface.set_sync_to_tracker(True)
                logger.info("Syncing Cover to Tracker.")
            else:
                # flank change 1 -> 0: stop macro
                self.plc_interface.set_sync_to_tracker(False)
                self.move_cover(0)
                logger.info("Closing Cover.")
                self.wait_for_cover_closing()

        # save the automation status for the next run
        self.last_cycle_automation_status = automation_should_be_running

        if (not automation_should_be_running) & (not self.plc_state.state.rain):
            if not self.plc_state.state.cover_closed:
                logger.info("Cover is still open. Trying to close again.")
                self.move_cover(0)
                self.wait_for_cover_closing()

        # read current state of actors and sensors in enclosure
        logger.info("New continuous readings.")
        StateInterface.update({"enclosure_plc_readings": self.plc_state})

        # possibly powerup/down spectrometer
        self.auto_set_power_spectrometer()

    # PLC.ACTORS SETTERS

    def move_cover(self, value):
        logger.debug(f"Received request to move cover to position {value} degrees.")

        # rain check before moving cover. PLC will deny cover requests during rain anyway
        if self.plc_state.state.rain:
            logger.debug("Denied to move cover due to rain detected.")
        else:
            self.plc_interface.set_manual_control(True)
            self.plc_interface.set_cover_angle(value)
            self.plc_interface.set_manual_control(False)

    def force_cover_close(self):
        if self.plc_state.state.reset_needed:
            self.plc_interface.reset()

        self.plc_interface.set_sync_to_tracker(False)
        self.move_cover(0)
        self.wait_for_cover_closing()

    def wait_for_cover_closing(self):
        """Waits steps of 5s for the enclosure cover to close.

        Raises the custom error CoverError if clover doesn't close in a given
        period of time.
        """

        start_time = time.time()

        while True:
            time.sleep(5)

            if self.plc_interface.cover_is_closed():
                break

            elapsed_time = time.time() - start_time
            if elapsed_time > 31:
                raise CoverError("Enclosure cover might be stuck.")

    def auto_set_power_spectrometer(self):
        """
        Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """

        current_sun_elevation = Astronomy.get_current_sun_elevation()
        min_power_elevation = self.config["tum_plc"]["min_power_elevation"] * astropy_units.deg

        # TODO: bind self.spectrometer_has_power to plc-read function

        if current_sun_elevation is not None:
            sun_is_above_minimum = current_sun_elevation >= min_power_elevation
            if sun_is_above_minimum and (not self.spectrometer_has_power):
                self.plc_interface.set_power_spectrometer(True)
                logger.info("Powering up the spectrometer.")
            if (not sun_is_above_minimum) and self.spectrometer_has_power:
                self.plc_interface.set_power_spectrometer(False)
                logger.info("Powering down the spectrometer.")
