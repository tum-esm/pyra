import time
from packages.core.utils import StateInterface, Logger, Astronomy, PLCError, PLCInterface

logger = Logger(origin="enclosure-control")


class CoverError(Exception):
    pass


class MotorFailedError(Exception):
    pass


class EnclosureControl:
    """
    https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
    """

    def __init__(self, initial_config: dict):
        self.config = initial_config
        self.initialized = False
        if self.config["general"]["test_mode"]:
            return

        if self.config["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        self._initialize()

    def _initialize(self):
        self.plc_interface = PLCInterface(self.config)
        self.plc_interface.connect()
        self.plc_interface.set_auto_temperature(True)
        self.plc_state = self.plc_interface.read()
        self.plc_interface.disconnect()
        self.last_cycle_automation_status = 0
        self.initialized = True

    def run(self, new_config: dict) -> None:
        self.config = new_config
        self.plc_interface.connect()

        if self.config["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        if self.config["general"]["test_mode"]:
            logger.debug("Skipping EnclosureControl in test mode")
            return

        logger.info("Running EnclosureControl")

        # get the latest PLC interface state and update with current config
        if self.initialized:
            self.plc_state = self.plc_interface.read()
        else:
            self._initialize()

        self.plc_interface.update_config(self.config)

        # read current state of actors and sensors in enclosure
        logger.info("New continuous readings.")
        StateInterface.update({"enclosure_plc_readings": self.plc_state.to_dict()})

        if self.config["tum_plc"]["controlled_by_user"]:
            logger.debug("Skipping EnclosureControl because enclosure is controlled by user")
            return

        # dawn/dusk detection: powerup/down spectrometer
        self.auto_set_power_spectrometer()

        if self.plc_state.state.motor_failed:
            raise MotorFailedError("URGENT: stop all actions, check cover in person")

        # check PLC ip connection (single ping)
        if self.plc_interface.is_responsive():
            logger.debug("Successful ping to PLC.")
        else:
            logger.warning("Could not ping PLC.")

        # check for automation state flank changes
        self.measurements_should_be_running = StateInterface.read()[
            "measurements_should_be_running"
        ]
        self.sync_cover_to_measurement_status()

        # save the automation status for the next run
        self.last_cycle_automation_status = self.measurements_should_be_running

        # verify cover position for every loop. Close cover if supposed to be closed.
        self.verify_cover_position()

        # verify that sync_to_cover status is still synced with measurement status
        self.verify_cover_sync()

        # disconnect from PLC
        self.plc_interface.disconnect()

    # PLC.ACTORS SETTERS

    def move_cover(self, value) -> None:
        logger.debug(f"Received request to move cover to position {value} degrees.")

        # rain check before moving cover. PLC will deny cover requests during rain anyway
        if self.plc_state.state.rain:
            logger.debug("Denied to move cover due to rain detected.")
        else:
            self.plc_interface.set_manual_control(True)
            self.plc_interface.set_cover_angle(value)
            self.plc_interface.set_manual_control(False)

    def force_cover_close(self) -> None:
        if self.plc_state.state.reset_needed:
            self.plc_interface.reset()

        self.plc_interface.set_sync_to_tracker(False)
        self.plc_interface.set_manual_control(True)
        self.plc_interface.set_cover_angle(0)
        self.plc_interface.set_manual_control(False)

    def wait_for_cover_closing(self, throw_error=True) -> None:
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
                if throw_error:
                    raise CoverError("Enclosure cover might be stuck.")
                break

    def auto_set_power_spectrometer(self) -> None:
        """
        Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """

        current_sun_elevation = Astronomy.get_current_sun_elevation()
        min_power_elevation = self.config["tum_plc"]["min_power_elevation"] * Astronomy.units.deg

        if current_sun_elevation is not None:
            sun_is_above_minimum = current_sun_elevation >= min_power_elevation
            if sun_is_above_minimum and (not self.plc_state.power.spectrometer):
                self.plc_interface.set_power_spectrometer(True)
                logger.info("Powering up the spectrometer.")
            if (not sun_is_above_minimum) and self.plc_state.power.spectrometer:
                self.plc_interface.set_power_spectrometer(False)
                logger.info("Powering down the spectrometer.")

    def sync_cover_to_measurement_status(self) -> None:
        if self.last_cycle_automation_status != self.measurements_should_be_running:
            if self.measurements_should_be_running:
                # flank change 0 -> 1: set cover mode: sync to tracker
                if self.plc_state.state.reset_needed:
                    self.plc_interface.reset()
                    time.sleep(10)
                if not self.plc_state.state.rain:
                    self.plc_interface.set_sync_to_tracker(True)
                logger.info("Syncing Cover to Tracker.")
            else:
                # flank change 1 -> 0: remove cover mode: sync to tracker, close cover
                self.plc_interface.set_sync_to_tracker(False)
                self.move_cover(0)
                logger.info("Closing Cover.")
                self.wait_for_cover_closing(throw_error=False)

    def verify_cover_position(self) -> None:
        if (not self.measurements_should_be_running) & (not self.plc_state.state.rain):
            if not self.plc_state.state.cover_closed:
                logger.info("Cover is still open. Trying to close again.")
                self.force_cover_close()
                self.wait_for_cover_closing()

    def verify_cover_sync(self) -> None:
        if self.measurements_should_be_running & (not self.plc_state.control.sync_to_tracker):
            logger.debug("Set sync to tracker to True to match measurement status.")
            self.plc_interface.set_sync_to_tracker(True)
        if (not self.measurements_should_be_running) & self.plc_state.control.sync_to_tracker:
            logger.debug("Set sync to tracker to False to match measurement status.")
            self.plc_interface.set_sync_to_tracker(False)
