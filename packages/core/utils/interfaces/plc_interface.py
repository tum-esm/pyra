import dataclasses
from typing import Any, Literal, Optional
import snap7  # type: ignore
import time
import os
from snap7.exceptions import Snap7Exception  # type: ignore
from packages.core.utils import Logger, StateInterface, types
from .plc_specification import PLC_SPECIFICATION_VERSIONS

logger = Logger(origin="plc-interface")
dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))

# used when initializing the state.json file
EMPTY_PLC_STATE: types.PlcStateDict = {
    "actors": {
        "fan_speed": None,
        "current_angle": None,
    },
    "control": {
        "auto_temp_mode": None,
        "manual_control": None,
        "manual_temp_mode": None,
        "sync_to_tracker": None,
    },
    "sensors": {
        "humidity": None,
        "temperature": None,
    },
    "state": {
        "cover_closed": None,
        "motor_failed": None,
        "rain": None,
        "reset_needed": None,
        "ups_alert": None,
    },
    "power": {
        "camera": None,
        "computer": None,
        "heater": None,
        "router": None,
        "spectrometer": None,
    },
    "connections": {
        "camera": None,
        "computer": None,
        "heater": None,
        "router": None,
        "spectrometer": None,
    },
}


class PLCInterface:
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
        self.specification = PLC_SPECIFICATION_VERSIONS[plc_version]

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
            self.connect()

    def connect(self) -> None:
        """
        Connects to the PLC Snap7. Times out after 30 seconds.
        """
        self.plc = snap7.client.Client()
        start_time = time.time()

        while True:
            try:
                if (time.time() - start_time) > 30:
                    raise Snap7Exception("Connect to PLC timed out.")

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
        return self.__read_bool(self.specification.state.rain)

    def cover_is_closed(self) -> bool:
        """
        Reads the single value "state.cover_closed"
        """
        return self.__read_bool(self.specification.state.cover_closed)

    def reset_is_needed(self) -> bool:
        """
        Reads the single value "state.reset_needed"
        """
        return self.__read_bool(self.specification.state.reset_needed)

    def get_cover_angle(self) -> int:
        """
        Reads the single value "actors.current_angle"
        """
        return self.__read_int(self.specification.actors.current_angle)

    # BULK READ

    def read(self) -> types.PlcStateDict:
        """
        Read the whole state of the PLC
        """

        # TODO: self.plc.read_multi_vars()

        plc_db_content: dict[int, int] = {}
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

        return {
            "actors": {
                "fan_speed": _get_int(s.actors.fan_speed),
                "current_angle": _get_int(s.actors.current_angle),
            },
            "control": {
                "auto_temp_mode": _get_bool(s.control.auto_temp_mode),
                "manual_control": _get_bool(s.control.manual_control),
                "manual_temp_mode": _get_bool(s.control.manual_temp_mode),
                "sync_to_tracker": _get_bool(s.control.sync_to_tracker),
            },
            "sensors": {
                "humidity": _get_int(s.sensors.humidity),
                "temperature": _get_int(s.sensors.temperature),
            },
            "state": {
                "cover_closed": _get_bool(s.state.cover_closed),
                "motor_failed": _get_bool(s.state.motor_failed),
                "rain": _get_bool(s.state.rain),
                "reset_needed": _get_bool(s.state.reset_needed),
                "ups_alert": _get_bool(s.state.ups_alert),
            },
            "power": {
                "camera": _get_bool(s.power.camera),
                "computer": _get_bool(s.power.computer),
                "heater": _get_bool(s.power.heater),
                "router": _get_bool(s.power.router),
                "spectrometer": _get_bool(s.power.spectrometer),
            },
            "connections": {
                "camera": _get_bool(s.connections.camera),
                "computer": _get_bool(s.connections.computer),
                "heater": _get_bool(s.connections.heater),
                "router": _get_bool(s.connections.router),
                "spectrometer": _get_bool(s.connections.spectrometer),
            },
        }

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

    def __update_bool(
        self, new_state: bool, spec: list[int], partial_plc_state: types.PlcStateDictPartial
    ) -> None:
        """
        1. low-level direct-write new_state to PLC according to spec
        2. low-level direct-read of plc's value according to spec
        3. raise PLCInterface.PLCError if value is different
        4. write update to StateInterface if update was successful
        """
        self.__write_bool(spec, new_state)
        if self.__read_bool(spec) != new_state:
            raise PLCInterface.PLCError("PLC state did not change")

        # TODO: check whether this results in a circular import
        StateInterface.update({"enclosure_plc_readings": partial_plc_state})

    def set_power_camera(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.power.camera,
            {"power": {"camera": new_state}},
        )

    def set_power_computer(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        assert self.specification.power.computer is not None
        self.__update_bool(
            new_state,
            self.specification.power.computer,
            {"power": {"computer": new_state}},
        )

    def set_power_heater(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.power.heater,
            {"power": {"heater": new_state}},
        )

    def set_power_router(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        assert self.specification.power.router is not None
        self.__update_bool(
            new_state,
            self.specification.power.router,
            {"power": {"router": new_state}},
        )

    def set_power_spectrometer(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.power.spectrometer,
            {"power": {"spectrometer": new_state}},
        )

    # PLC.CONTROL SETTERS

    def set_sync_to_tracker(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.control.sync_to_tracker,
            {"control": {"sync_to_tracker": new_state}},
        )

    def set_manual_control(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.control.manual_control,
            {"control": {"manual_control": new_state}},
        )

    def set_auto_temperature(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.control.auto_temp_mode,
            {"control": {"auto_temp_mode": new_state}},
        )

    def set_manual_temperature(self, new_state: bool) -> None:
        """Raises PLCInterface.PLCError, if value hasn't been changed"""
        self.__update_bool(
            new_state,
            self.specification.control.manual_temp_mode,
            {"control": {"manual_temp_mode": new_state}},
        )

    def reset(self) -> None:
        """Does not check, whether the value has been changed"""
        if self.plc_version == 1:
            self.__write_bool(self.specification.control.reset, False)
        else:
            self.__write_bool(self.specification.control.reset, True)

    # PLC.ACTORS SETTERS

    def set_cover_angle(self, value: int) -> None:
        """Does not check, whether the value has been changed"""
        self.__write_int(self.specification.actors.move_cover, value)
