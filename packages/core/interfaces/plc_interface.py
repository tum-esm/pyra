from datetime import datetime
from typing import Literal, Optional
import snap7
import time
import os
from snap7.exceptions import Snap7Exception
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="plc-interface")

_PLC_SPECIFICATION_VERSIONS: dict[Literal[1, 2], types.PlcSpecificationDict] = {
    1: {
        "actors": {
            "current_angle": [25, 6, 2],
            "fan_speed": [8, 18, 2],
            "move_cover": [25, 8, 2],
            "nominal_angle": [25, 8, 2],
        },
        "control": {
            "auto_temp_mode": [8, 24, 1, 2],
            "manual_control": [8, 24, 1, 5],
            "manual_temp_mode": [8, 24, 1, 3],
            "reset": [3, 4, 1, 5],
            "sync_to_tracker": [8, 16, 1, 0],
        },
        "sensors": {"humidity": [8, 22, 2], "temperature": [8, 20, 2]},
        "state": {
            "cover_closed": [25, 2, 1, 2],
            "motor_failed": [8, 12, 1, 3],
            "rain": [8, 6, 1, 0],
            "reset_needed": [3, 2, 1, 2],
            "ups_alert": [8, 0, 1, 1],
        },
        "power": {
            "camera": [8, 16, 1, 2],
            "computer": [8, 16, 1, 6],
            "heater": [8, 16, 1, 5],
            "router": [8, 16, 1, 3],
            "spectrometer": [8, 16, 1, 1],
        },
        "connections": {
            "camera": [8, 14, 1, 6],
            "computer": [8, 14, 1, 3],
            "heater": [8, 14, 1, 1],
            "router": [8, 14, 1, 2],
            "spectrometer": [8, 14, 1, 0],
        },
    },
    2: {
        "actors": {
            "current_angle": [6, 6, 2],
            "fan_speed": [8, 4, 2],
            "move_cover": [6, 8, 2],
            "nominal_angle": [6, 8, 2],
        },
        "control": {
            "auto_temp_mode": [8, 24, 1, 5],
            "manual_control": [8, 12, 1, 7],
            "manual_temp_mode": [8, 24, 1, 4],
            "reset": [3, 4, 1, 5],
            "sync_to_tracker": [8, 8, 1, 1],
        },
        "sensors": {"humidity": [8, 22, 2], "temperature": [8, 16, 2]},
        "state": {
            "cover_closed": [6, 16, 1, 1],
            "motor_failed": None,
            "rain": [3, 0, 1, 0],
            "reset_needed": [3, 2, 1, 2],
            "ups_alert": [8, 13, 1, 6],
        },
        "power": {
            "camera": [8, 8, 1, 4],  # K5 Relay
            "computer": None,
            "heater": [8, 12, 1, 7],  # K3 Relay
            "router": None,  # not allowed
            "spectrometer": [8, 8, 1, 2],  # K4 Relay
        },
        "connections": {
            "camera": None,
            "computer": [8, 13, 1, 2],
            "heater": [8, 6, 1, 1],
            "router": [8, 12, 1, 4],
            "spectrometer": None,
        },
    },
}


class PLCInterface:
    """Uses the snap7 library to connect to the Siemens PLC operating the
    enclosure hardware.

    Manual: https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
    """

    @staticmethod
    class PLCError(Exception):
        """
        Raised when updating a boolean value on the
        plc did not change its internal value.

        Can originate from:
        * set_power_camera/_computer/_heater/_router/_spectrometer
        * set_sync_to_tracker/_manual_control
        * set_auto_temperature/_manual_temperature
        """

    def __init__(self, plc_version: Literal[1, 2], plc_ip: str) -> None:
        self.plc_version = plc_version
        self.plc_ip = plc_ip
        self.specification = _PLC_SPECIFICATION_VERSIONS[plc_version]

    # CONNECTION/CLASS MANAGEMENT

    def update_config(self, new_plc_version: Literal[1, 2], new_plc_ip: str) -> None:
        """
        Update the internally used config (executed at the)
        beginning of enclosure-control's run-function.

        Reconnecting to PLC, when IP has changed.
        """
        if (self.plc_version != new_plc_version) or (self.plc_ip != new_plc_ip):
            logger.debug("PLC ip has changed, reconnecting now")
            self.disconnect()
            self.plc_version = new_plc_version
            self.plc_ip = new_plc_ip
            self.specification = _PLC_SPECIFICATION_VERSIONS[self.plc_version]
            self.connect()

    def connect(self) -> None:
        """
        Connects to the PLC Snap7. Times out after 30 seconds.
        """
        self.plc = snap7.client.Client()
        start_time = time.time()

        while True:
            if (time.time() - start_time) > 30:
                raise Snap7Exception("Connect to PLC timed out.")

            try:
                self.plc.connect(self.plc_ip, 0, 1)
                time.sleep(0.2)

                if self.plc.get_connected():
                    logger.debug("Connected to PLC.")
                    return

                self.plc.destroy()
                self.plc = snap7.client.Client()

            except Snap7Exception:
                self.plc.destroy()
                self.plc = snap7.client.Client()

    def disconnect(self) -> None:
        """
        Disconnects from the PLC Snap7
        """
        try:
            self.plc.disconnect()
            self.plc.destroy()
            logger.debug("Gracefully disconnected from PLC.")
        except Snap7Exception:
            self.plc.destroy()
            logger.debug("Disconnected ungracefully from PLC.")

    def is_responsive(self) -> bool:
        """Pings the PLC"""
        return os.system("ping -n 1 " + self.plc_ip) == 0

    # DIRECT READ FUNCTIONS

    def rain_is_detected(self) -> bool:
        """
        Reads the single value "state.rain"
        """
        return self.__read_bool(self.specification["state"]["rain"])

    def cover_is_closed(self) -> bool:
        """
        Reads the single value "state.cover_closed"
        """
        return self.__read_bool(self.specification["state"]["cover_closed"])

    def reset_is_needed(self) -> bool:
        """
        Reads the single value "state.reset_needed"
        """
        return self.__read_bool(self.specification["state"]["reset_needed"])

    def get_cover_angle(self) -> int:
        """
        Reads the single value "actors.current_angle"
        """
        return self.__read_int(self.specification["actors"]["current_angle"])

    # BULK READ

    def read(self) -> types.PlcState:
        """
        Read the whole state of the PLC
        """

        plc_db_content: dict[int, bytearray] = {}
        plc_db_size = {1: {3: 6, 8: 26, 25: 10}, 2: {3: 5, 6: 17, 8: 25}}[self.plc_version]

        for db_index, db_size in plc_db_size.items():
            plc_db_content[db_index] = self.plc.db_read(db_index, 0, db_size)
            self.__sleep_while_cpu_is_busy()

        logger.debug(f"new plc bulk read: {plc_db_content}")

        def _get_int(spec: Optional[list[int]]) -> Optional[int]:
            if spec is None:
                return None
            return snap7.util.get_int(plc_db_content[spec[0]], spec[1])  # type: ignore

        def _get_bool(spec: Optional[list[int]]) -> Optional[bool]:
            if spec is None:
                return None
            return snap7.util.get_bool(plc_db_content[spec[0]], spec[1], spec[3])  # type: ignore

        s = self.specification

        return types.PlcState(
            **{
                "last_read_time": datetime.now().strftime("%H:%M:%S"),
                "actors": {
                    "fan_speed": _get_int(s["actors"]["fan_speed"]),
                    "current_angle": _get_int(s["actors"]["current_angle"]),
                },
                "control": {
                    "auto_temp_mode": _get_bool(s["control"]["auto_temp_mode"]),
                    "manual_control": _get_bool(s["control"]["manual_control"]),
                    "manual_temp_mode": _get_bool(s["control"]["manual_temp_mode"]),
                    "sync_to_tracker": _get_bool(s["control"]["sync_to_tracker"]),
                },
                "sensors": {
                    "humidity": _get_int(s["sensors"]["humidity"]),
                    "temperature": _get_int(s["sensors"]["temperature"]),
                },
                "state": {
                    "cover_closed": _get_bool(s["state"]["cover_closed"]),
                    "motor_failed": _get_bool(s["state"]["motor_failed"]),
                    "rain": _get_bool(s["state"]["rain"]),
                    "reset_needed": _get_bool(s["state"]["reset_needed"]),
                    "ups_alert": _get_bool(s["state"]["ups_alert"]),
                },
                "power": {
                    "camera": _get_bool(s["power"]["camera"]),
                    "computer": _get_bool(s["power"]["computer"]),
                    "heater": _get_bool(s["power"]["heater"]),
                    "router": _get_bool(s["power"]["router"]),
                    "spectrometer": _get_bool(s["power"]["spectrometer"]),
                },
                "connections": {
                    "camera": _get_bool(s["connections"]["camera"]),
                    "computer": _get_bool(s["connections"]["computer"]),
                    "heater": _get_bool(s["connections"]["heater"]),
                    "router": _get_bool(s["connections"]["router"]),
                    "spectrometer": _get_bool(s["connections"]["spectrometer"]),
                },
            }
        )

    # LOW LEVEL READ FUNCTIONS

    def __sleep_while_cpu_is_busy(self) -> None:
        """
        Initially sleeps 0.5 seconds. The checks every 2 seconds
        whether the CPU of the PLC is still busy. End function
        if the CPU is idle again.
        """
        time.sleep(0.5)
        if str(self.plc.get_cpu_state()) == "S7CpuStatusRun":
            time.sleep(2)

    def __read_int(self, action: list[int]) -> int:
        """
        Reads an INT value in the PLC database.

        action is tuple: db_number, start, size
        """
        assert len(action) == 3

        msg: bytearray = self.plc.db_read(*action)
        value: int = snap7.util.get_int(msg, 0)

        self.__sleep_while_cpu_is_busy()

        return value

    def __write_int(self, action: list[int], value: int) -> None:
        """Changes an INT value in the PLC database."""
        assert len(action) == 3
        db_number, start, size = action

        msg = bytearray(size)
        snap7.util.set_int(msg, 0, value)
        self.plc.db_write(db_number, start, msg)

        self.__sleep_while_cpu_is_busy()

    def __read_bool(self, action: list[int]) -> bool:
        """Reads a BOOL value in the PLC database."""
        assert len(action) == 4
        db_number, start, size, bool_index = action

        msg: bytearray = self.plc.db_read(db_number, start, size)
        value: bool = snap7.util.get_bool(msg, 0, bool_index)

        self.__sleep_while_cpu_is_busy()

        return value

    def __write_bool(self, action: list[int], value: bool) -> None:
        """Changes a BOOL value in the PLC database."""
        assert len(action) == 4
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        snap7.util.set_bool(msg, 0, bool_index, value)
        self.plc.db_write(db_number, start, msg)

        self.__sleep_while_cpu_is_busy()

    # PLC.POWER SETTERS

    def __update_bool(self, new_state: bool, spec: list[int]) -> None:
        """
        1. low-level direct-write new_state to PLC according to spec
        2. low-level direct-read of plc's value according to spec
        3. raise `PLCInterface.PLCError` if value is different
        """
        self.__write_bool(spec, new_state)
        if self.__read_bool(spec) != new_state:
            raise PLCInterface.PLCError("PLC state did not change")

    def set_power_camera(self, new_state: bool) -> None:
        """Raises `PLCInterface.PLCError`, if value hasn't been changed"""

        self.__update_bool(new_state, self.specification["power"]["camera"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.power.camera = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_power_computer(self, new_state: bool) -> None:
        """Raises `PLCInterface.PLCError`, if value hasn't been changed"""
        assert self.specification["power"]["computer"] is not None

        self.__update_bool(new_state, self.specification["power"]["computer"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.power.computer = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_power_heater(self, new_state: bool) -> None:
        """Raises `PLCInterface.PLCError`, if value hasn't been changed"""

        self.__update_bool(new_state, self.specification["power"]["heater"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.power.heater = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_power_router(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""

        assert self.specification["power"]["router"] is not None
        self.__update_bool(new_state, self.specification["power"]["router"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.power.router = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_power_spectrometer(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""

        self.__update_bool(new_state, self.specification["power"]["spectrometer"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.power.spectrometer = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    # PLC.CONTROL SETTERS

    def set_sync_to_tracker(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(new_state, self.specification["control"]["sync_to_tracker"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.control.sync_to_tracker = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_manual_control(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(new_state, self.specification["control"]["manual_control"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.control.manual_control = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_auto_temperature(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(new_state, self.specification["control"]["auto_temp_mode"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.control.auto_temp_mode = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def set_manual_temperature(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(new_state, self.specification["control"]["manual_temp_mode"])

        def apply_state_update(state: types.State) -> types.State:
            state.enclosure_plc_readings.control.manual_temp_mode = new_state
            return state

        interfaces.StateInterface.update(apply_state_update)

    def reset(self) -> None:
        """Does not check, whether the value has been changed"""
        if self.plc_version == 1:
            self.__write_bool(self.specification["control"]["reset"], False)
        else:
            self.__write_bool(self.specification["control"]["reset"], True)

    # PLC.ACTORS SETTERS

    def set_cover_angle(self, value: int) -> None:
        """Does not check, whether the value has been changed"""
        self.__write_int(self.specification["actors"]["move_cover"], value)
