import dataclasses
import json
import snap7
import time
import os
from packages.core.utils import Logger, with_filelock, update_dict_recursively
from .plc_specification import PLC_SPECIFICATION_VERSIONS

logger = Logger(origin="pyra.core.enclosure-control")
dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))


class PLCError(Exception):
    pass


@dataclasses.dataclass
class PLCActorsState:
    current_angle: int = None
    fan_speed: int = None


@dataclasses.dataclass
class PLCControlState:
    auto_temp_mode: bool = None
    manual_control: bool = None
    manual_temp_mode: bool = None
    sync_to_tracker: bool = None


@dataclasses.dataclass
class PLCSensorsState:
    humidity: int = None
    temperature: int = None


@dataclasses.dataclass
class PLCStateState:
    cover_closed: bool = None
    motor_failed: bool = None
    rain: bool = None
    reset_needed: bool = None
    ups_alert: bool = None


@dataclasses.dataclass
class PLCPowerState:
    camera: bool = None
    computer: bool = None
    heater: bool = None
    router: bool = None
    spectrometer: bool = None


@dataclasses.dataclass
class PLCConnectionsState:
    camera: bool = None
    computer: bool = None
    heater: bool = None
    router: bool = None
    spectrometer: bool = None


@dataclasses.dataclass
class PLCState:
    actors: PLCActorsState
    control: PLCControlState
    sensors: PLCSensorsState
    state: PLCStateState
    power: PLCPowerState
    connections: PLCConnectionsState

    def to_dict(self):
        out = {}
        for field in dataclasses.fields(self):
            field_value = getattr(self, field.name)
            if field_value is not None:
                field_value = getattr(self, field.name).__dict__
            out[field.name] = field_value
        return out


EMPTY_PLC_STATE = PLCState(
    actors=PLCActorsState(),
    control=PLCControlState(),
    sensors=PLCSensorsState(),
    state=PLCStateState(),
    power=PLCPowerState(),
    connections=PLCConnectionsState(),
)


# This duplication is required in order top prevent circular imports
STATE_LOCK_PATH = os.path.join(PROJECT_DIR, "config", ".state.lock")
RUNTIME_DATA_PATH = os.path.join(PROJECT_DIR, "runtime-data")
STATE_FILE_PATH = os.path.join(RUNTIME_DATA_PATH, "state.json")


@with_filelock(STATE_LOCK_PATH)
def update_state_file(update: dict):
    with open(STATE_FILE_PATH, "r") as f:
        current_state = json.load(f)

    new_state = update_dict_recursively(current_state, update)
    with open(STATE_FILE_PATH, "w") as f:
        json.dump(new_state, f, indent=4)


class PLCInterface:
    def __init__(self, config: dict):
        self.config = config
        self.specification = PLC_SPECIFICATION_VERSIONS[config["tum_plc"]["version"]]

        self.plc = snap7.client.Client()
        self._connect()

    # CONNECTION

    def update_config(self, new_config: dict):
        if self.config["tum_plc"]["ip"] != new_config["tum_plc"]["ip"]:
            logger.debug("PLC ip has changed, reconnecting now")
            self._disconnect()

        self.config = new_config
        if not self._is_connected():
            self._connect()

    def _connect(self) -> None:
        """
        Connects to the PLC Snap7
        """
        self.plc.connect(self.config["tum_plc"]["ip"], 0, 1)

        if not self._is_connected():
            raise PLCError("Could not connect to PLC")

    def _disconnect(self) -> None:
        """
        Disconnects from the PLC Snap7
        """
        self.plc.disconnect()

        if self._is_connected():
            raise PLCError("Could not disconnect from PLC")

    def _is_connected(self) -> bool:
        """
        Checks whether PLC is connected
        """
        return self.plc.get_connected()

    def is_responsive(self) -> bool:
        """Pings the PLC"""
        return os.system("ping -n 1 " + self.config["tum_plc"]["ip"]) == 0

    # def rain_is_detected(self) -> bool:
    #    return self._read_bool(self.specification.state.rain)

    def cover_is_closed(self) -> bool:
        return self._read_bool(self.specification.state.cover_closed)

    def reset_is_needed(self) -> bool:
        return self._read_bool(self.specification.state.reset_needed)

    def get_cover_angle(self) -> int:
        return self._read_int(self.specification.actors.current_angle)

    def read(self) -> PLCState:
        """
        Read the whole state of the PLC
        """

        plc_db_content = {}
        plc_db_content[8] = self.plc.db_read(8, 0, 25)
        self._sleep_while_cpu_is_busy()
        plc_db_content[25] = self.plc.db_read(25, 0, 9)
        self._sleep_while_cpu_is_busy()
        plc_db_content[3] = self.plc.db_read(3, 0, 5)
        self._sleep_while_cpu_is_busy()

        def _get_int(spec: list[int]) -> int:
            return snap7.util.get_int(plc_db_content[spec[0]], spec[1])

        def _get_bool(spec: list[int]) -> bool:
            return snap7.util.get_bool(plc_db_content[spec[0]], spec[1], spec[3])

        return PLCState(
            actors=PLCActorsState(
                fan_speed=_get_int(self.specification.actors.fan_speed),
                current_angle=_get_int(self.specification.actors.current_angle),
            ),
            control=PLCControlState(
                auto_temp_mode=_get_bool(self.specification.control.auto_temp_mode),
                manual_control=_get_bool(self.specification.control.manual_control),
                manual_temp_mode=_get_bool(self.specification.control.manual_temp_mode),
                sync_to_tracker=_get_bool(self.specification.control.sync_to_tracker),
            ),
            sensors=PLCSensorsState(
                humidity=_get_int(self.specification.sensors.humidity),
                temperature=_get_int(self.specification.sensors.temperature),
            ),
            state=PLCStateState(
                cover_closed=_get_bool(self.specification.state.cover_closed),
                motor_failed=_get_bool(self.specification.state.motor_failed),
                rain=_get_bool(self.specification.state.rain),
                reset_needed=_get_bool(self.specification.state.reset_needed),
                ups_alert=_get_bool(self.specification.state.ups_alert),
            ),
            power=PLCPowerState(
                camera=_get_bool(self.specification.power.camera),
                computer=_get_bool(self.specification.power.computer),
                heater=_get_bool(self.specification.power.heater),
                router=_get_bool(self.specification.power.router),
                spectrometer=_get_bool(self.specification.power.spectrometer),
            ),
            connections=PLCConnectionsState(
                camera=_get_bool(self.specification.connections.camera),
                computer=_get_bool(self.specification.connections.computer),
                heater=_get_bool(self.specification.connections.heater),
                router=_get_bool(self.specification.connections.router),
                spectrometer=_get_bool(self.specification.connections.spectrometer),
            ),
        )

    def _sleep_while_cpu_is_busy(self) -> None:
        time.sleep(0.2)
        if str(self.plc.get_cpu_state()) == "S7CpuStatusRun":
            time.sleep(1.5)

    def _read_int(self, action: list[int]) -> int:
        """Reads an INT value in the PLC database."""
        assert len(action) == 3
        db_number, start, size = action

        msg = self.plc.db_read(db_number, start, size)
        value = snap7.util.get_int(msg, 0)

        self._sleep_while_cpu_is_busy()

        return value

    def _write_int(self, action: list[int], value: int) -> None:
        """Changes an INT value in the PLC database."""
        assert len(action) == 3
        db_number, start, size = action

        msg = bytearray(size)
        snap7.util.set_int(msg, 0, value)
        self.plc.db_write(db_number, start, msg)

        self._sleep_while_cpu_is_busy()

    def _read_bool(self, action: list[int]) -> bool:
        """Reads a BOOL value in the PLC database."""
        assert len(action) == 4
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        value = snap7.util.get_bool(msg, 0, bool_index)

        self._sleep_while_cpu_is_busy()

        return value

    def _write_bool(self, action: list[int], value: bool) -> None:
        """Changes a BOOL value in the PLC database."""
        assert len(action) == 4
        db_number, start, size, bool_index = action

        msg = self.plc.db_read(db_number, start, size)
        snap7.util.set_bool(msg, 0, bool_index, value)
        self.plc.db_write(db_number, start, msg)

        self._sleep_while_cpu_is_busy()

    # PLC.POWER SETTERS

    def set_power_camera(self, new_state: bool) -> None:
        self._write_bool(self.specification.power.camera, new_state)
        if self._read_bool(self.specification.power.camera) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file({"enclosure_plc_readings": {"power": {"camera": new_state}}})

    def set_power_computer(self, new_state: bool) -> None:
        self._write_bool(self.specification.power.computer, new_state)
        if self._read_bool(self.specification.power.computer) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file({"enclosure_plc_readings": {"power": {"computer": new_state}}})

    def set_power_heater(self, new_state: bool) -> None:
        self._write_bool(self.specification.power.heater, new_state)
        if self._read_bool(self.specification.power.heater) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file({"enclosure_plc_readings": {"power": {"heater": new_state}}})

    def set_power_router(self, new_state: bool) -> None:
        self._write_bool(self.specification.power.router, new_state)
        if self._read_bool(self.specification.power.router) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file({"enclosure_plc_readings": {"power": {"router": new_state}}})

    def set_power_spectrometer(self, new_state: bool) -> None:
        self._write_bool(self.specification.power.spectrometer, new_state)
        if self._read_bool(self.specification.power.spectrometer) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file({"enclosure_plc_readings": {"power": {"spectrometer": new_state}}})

    # PLC.CONTROL SETTERS

    def set_sync_to_tracker(self, new_state: bool) -> None:
        self._write_bool(self.specification.control.sync_to_tracker, new_state)
        if self._read_bool(self.specification.control.sync_to_tracker) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file(
            {"enclosure_plc_readings": {"control": {"sync_to_tracker": new_state}}}
        )

    def set_manual_control(self, new_state: bool) -> None:
        self._write_bool(self.specification.control.manual_control, new_state)
        if self._read_bool(self.specification.control.manual_control) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file(
            {"enclosure_plc_readings": {"control": {"manual_control": new_state}}}
        )

    def set_auto_temperature(self, new_state: bool) -> None:
        self._write_bool(self.specification.control.auto_temp_mode, new_state)
        if self._read_bool(self.specification.control.auto_temp_mode) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file(
            {"enclosure_plc_readings": {"control": {"auto_temp_mode": new_state}}}
        )

    def set_manual_temperature(self, new_state: bool) -> None:
        self._write_bool(self.specification.control.manual_temp_mode, new_state)
        if self._read_bool(self.specification.control.manual_temp_mode) != new_state:
            raise PLCError("PLC state did not change")
        update_state_file(
            {"enclosure_plc_readings": {"control": {"manual_temp_mode": new_state}}}
        )

    def reset(self) -> None:
        self._write_bool(self.specification.control.reset, False)

    # PLC.ACTORS SETTERS
    def set_cover_angle(self, value: int) -> None:
        self._write_int(self.specification.actors.move_cover, value)
