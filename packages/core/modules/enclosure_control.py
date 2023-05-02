import time
from snap7.exceptions import Snap7Exception
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="enclosure-control")


class EnclosureControl:
    """EnclosureControl allows to interact with TUM made weather protected
    enclosures that allow a 24/7 deployment of the FTIR spectrometer EM27/Sun
    in the field. The class takes the latest decision from
    `measurement_conditions.py` (StateInterface: measurements_should_be_running)
    and communicates with the enclosure's built in Siemens S7 PLC to read and
    write parameters to its database (PLCInterface). Additionally, it powers
    down the spectrometer during dusk to extend the overall spectrometer
    lifetime. During dawn, it powers up the spectrometer to prepare and warm it
    up for the next measurement day. At initialization, the PLC is set to control
    the ambient enclosure temperature in automatic mode. During flank changes of
    measurements_should_be_running it either tells the enclosure to open up the
    cover to allow direct sunlight to hit the CamTracker mirrors or close the
    cover to protect the instrument. Instrument protection from bad weather
    conditions is always prioritised over a slight maximization of measurement
    uptime."""

    @staticmethod
    class CoverError(Exception):
        pass

    @staticmethod
    class MotorFailedError(Exception):
        pass

    def __init__(self, initial_config: types.ConfigDict):
        self.config = initial_config
        self.initialized = False
        self.last_plc_connection_time = time.time()
        self.motor_reset_needed_in_last_iteration = False
        if self.config["general"]["test_mode"]:
            return

        if self.config["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

    def __initialize(self) -> None:
        """Initializes the default PLC settings at startup or activation in config."""
        assert self.config["tum_plc"] is not None

        self.plc_interface = interfaces.PLCInterface(
            self.config["tum_plc"]["version"], self.config["tum_plc"]["ip"]
        )
        self.plc_interface.connect()
        self.plc_interface.set_auto_temperature(True)
        self.plc_state = self.plc_interface.read()
        logger.debug("Finished initial PLC setup.")
        self.last_cycle_automation_status = 0
        self.initialized = True

    def run(self, new_config: types.ConfigDict) -> None:
        """Called in every cycle of the main loop.
        Updates enclosure state based on the current automation status.
        """
        self.config = new_config

        # Skips the rest of run if module not activated in config
        if self.config["tum_plc"] is None:
            logger.debug("Skipping EnclosureControl without a TUM PLC")
            return

        # Allows to run Pyra-4 without measurement system hardware present
        if self.config["general"]["test_mode"]:
            logger.debug("Skipping EnclosureControl in test mode")
            return

        logger.info("Running EnclosureControl")

        # Check for current measurement status
        self.measurements_should_be_running = interfaces.StateInterface.read()[
            "measurements_should_be_running"
        ]

        # Updates the current loop to the latest config.
        # Performs a connect to the PLC for the duration of this loop.
        # Initializes if first call of the module.
        try:
            if not self.initialized:
                self.__initialize()
            else:
                self.plc_interface.update_config(
                    self.config["tum_plc"]["version"], self.config["tum_plc"]["ip"]
                )
                self.plc_interface.connect()

            # Reads and returns the latest PLC database states
            try:
                self.plc_state = self.plc_interface.read()
            except Snap7Exception:
                logger.warning("Could not read PLC state in this loop.")

            # Push the latest readout of the PLC state to the StateInterface
            logger.info("New continuous readings.")
            interfaces.StateInterface.update({"enclosure_plc_readings": self.plc_state})

            # Check for critial error: Motor Failed Flag in PLC. In case of present
            # motor failed flag the cover might not be closed in bad weather
            # conditions. Potentially putting the measurement instrument at risk.
            if self.plc_state["state"]["motor_failed"]:
                if self.plc_state["state"]["reset_needed"] and (
                    not self.motor_reset_needed_in_last_iteration
                ):
                    # when both motor and reset flag are set, then a reset is probably
                    # needed - skipping this module until the next iteration
                    self.motor_reset_needed_in_last_iteration = True
                    self.plc_interface.reset()
                    return
                else:
                    # if the motor failed but no reset needed or if the reset has
                    # already been done in the last iteration, then this error will
                    # be raised (and an email sent out)
                    raise EnclosureControl.MotorFailedError(
                        "URGENT: stop all actions, check cover in person"
                    )
            else:
                self.motor_reset_needed_in_last_iteration = False

            # Skip writing to the PLC as the user took over control from the automation
            if self.config["tum_plc"]["controlled_by_user"]:
                logger.debug(
                    "Skipping EnclosureControl because enclosure is controlled by user"
                )
                return

            # Dawn/dusk detection: powerup/down spectrometer at a defined sun angle
            self.auto_set_power_spectrometer()

            # Check PLC ip connection (single ping).
            if self.plc_interface.is_responsive():
                logger.debug("Successful ping to PLC.")
            else:
                logger.warning("Could not ping PLC.")

            # Syncs the cover to the current automation status present
            self.sync_cover_to_measurement_status()

            # Verify functions will handle desync caused by a user taking over control in previous loops
            # Verify cover position for every loop. Close cover if supposed to be closed.
            self.verify_cover_position()

            # Verify that sync_to_cover status is still synced with measurement status
            self.verify_cover_sync()

            # Save the automation status for the next run. This allows for flank detection from previous completed loops.
            self.last_cycle_automation_status = self.measurements_should_be_running

            # Disconnect from PLC
            self.plc_interface.disconnect()
            self.last_plc_connection_time = time.time()

        # Allows for PLC connection downtime of 10 minutes before an error is raised.
        # Allows PLC connection to heal itself.
        except (Snap7Exception, RuntimeError) as e:
            logger.exception(e)
            now = time.time()
            seconds_since_error_occured = now - self.last_plc_connection_time
            if seconds_since_error_occured > 600:
                raise interfaces.PLCInterface.PLCError(
                    "Snap7Exception/RuntimeError persisting for 10+ minutes"
                )
            else:
                logger.info(
                    f"Snap7Exception/RuntimeError persisting for {round(seconds_since_error_occured/60, 2)}"
                    + " minutes. Sending email at 10 minutes."
                )

    # PLC.ACTORS SETTERS

    def move_cover(self, value: int) -> None:
        """Moves the cover attached on top of the enclosure. The cover is moved by a electrical
        motor controlled by the PLC. The cover functions as weather protection for the measurement
        instrument. In case of bad weather the PLC takes over control and closes the cover itself.
        A movement of the cover during bad weather conditions shall not be allowed as instrument
        saefty is priotized higher than maximization of overall measurement uptime.
        """
        logger.debug(f"Received request to move cover to position {value} degrees.")

        # rain check before moving cover. PLC will deny cover requests during rain anyway
        if self.plc_state["state"]["rain"]:
            logger.debug("Denied to move cover due to rain detected.")
        else:
            self.plc_interface.set_manual_control(True)
            self.plc_interface.set_cover_angle(value)
            self.plc_interface.set_manual_control(False)

    def force_cover_close(self) -> None:
        """Emergency option to call to ensure that the cover is closed immediately. Accounts for
        possible blocking conditions caused by the PLC internals:
        1. Reset needed
        2. Sync to tracker still active
        3. Manual control not active
        """
        if not self.initialized:
            self.__initialize()

        if self.plc_state["state"]["reset_needed"]:
            self.plc_interface.reset()

        self.plc_interface.set_sync_to_tracker(False)
        self.plc_interface.set_manual_control(True)
        self.plc_interface.set_cover_angle(0)
        self.plc_interface.set_manual_control(False)

    def wait_for_cover_closing(self, throw_error: bool = True) -> None:
        """Validates the progress of a cover closing call. Continues when cover is closed.
        Validation is done every 5s with a maximum waiting time of 60s.

        Raises the custom error CoverError if clover doesn't close in time.
        """

        start_time = time.time()
        while True:
            time.sleep(5)

            if self.plc_interface.cover_is_closed():
                break

            elapsed_time = time.time() - start_time
            if elapsed_time > 60:
                if throw_error:
                    raise EnclosureControl.CoverError("Enclosure cover might be stuck.")
                break

    def auto_set_power_spectrometer(self) -> None:
        """
        Shuts down spectrometer if the sun angle is too low. Starts up the
        spectrometer in the morning when minimum angle is satisfied.
        """

        current_sun_elevation = utils.Astronomy.get_current_sun_elevation(self.config)
        min_power_elevation = self.config["general"]["min_sun_elevation"] - 1
        sun_is_above_minimum = current_sun_elevation >= min_power_elevation
        spectrometer_is_powered = self.plc_state["power"]["spectrometer"]

        if sun_is_above_minimum and (not spectrometer_is_powered):
            self.plc_interface.set_power_spectrometer(True)
            logger.info("Powering up the spectrometer.")

        if (not sun_is_above_minimum) and spectrometer_is_powered:
            self.plc_interface.set_power_spectrometer(False)
            logger.info("Powering down the spectrometer.")

    def sync_cover_to_measurement_status(self) -> None:
        """Checks for flank changes in parameter measurement_should_be_running.
        Positive flank: Set sync_cover flag in PLC to start matching the Camtracker mirror position.
        Negative flank: Remove sync_cover flag in PLC and move cover to position 0.
        """
        if self.last_cycle_automation_status != self.measurements_should_be_running:
            if self.measurements_should_be_running:
                # flank change 0 -> 1: set cover mode: sync to tracker
                if self.plc_state["state"]["reset_needed"]:
                    self.plc_interface.reset()
                    time.sleep(10)
                if not self.plc_state["state"]["rain"]:
                    self.plc_interface.set_sync_to_tracker(True)
                logger.info("Syncing Cover to Tracker.")
            else:
                # flank change 1 -> 0: remove cover mode: sync to tracker, close cover
                if self.plc_state["state"]["reset_needed"]:
                    self.plc_interface.reset()
                    time.sleep(10)
                self.plc_interface.set_sync_to_tracker(False)
                self.move_cover(0)
                logger.info("Closing Cover.")
                self.wait_for_cover_closing(throw_error=False)

    def verify_cover_position(self) -> None:
        """Verifies that the cover is closed when measurements are currently not set to be running.
        Closed the cover in case of a mismatch.

        This functions allows to detect desync caused by previous user controlled decisions. It
        also functions as a failsafe to ensure weather protection of the instrument."""
        if (not self.measurements_should_be_running) & (not self.plc_state["state"]["rain"]):
            if not self.plc_state["state"]["cover_closed"]:
                logger.info("Cover is still open. Trying to close again.")
                self.force_cover_close()
                self.wait_for_cover_closing()

    def verify_cover_sync(self) -> None:
        """Syncs the current cover_sync flag in the PLC with the present measurement status.

        This functions allows to detect desync caused by previous user controlled decisions."""
        if self.measurements_should_be_running and (
            not self.plc_state["control"]["sync_to_tracker"]
        ):
            logger.debug("Set sync to tracker to True to match measurement status.")
            self.plc_interface.set_sync_to_tracker(True)
        if (not self.measurements_should_be_running) and self.plc_state["control"][
            "sync_to_tracker"
        ]:
            logger.debug("Set sync to tracker to False to match measurement status.")
            self.plc_interface.set_sync_to_tracker(False)
