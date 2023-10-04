from __future__ import annotations
from typing import Literal, Optional
import os
import pydantic
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, "config", "config.json")


class StrictFilePath(pydantic.RootModel):
    root: str

    @pydantic.field_validator('root')
    @classmethod
    def file_should_exist(cls, v: str) -> str:
        if not os.path.isfile(v):
            raise ValueError('File does not exist')
        return v


class StrictDirectoryPath(pydantic.RootModel):
    root: str

    @pydantic.field_validator('root')
    @classmethod
    def directory_should_exist(cls, v: str) -> str:
        if not os.path.isdir(v):
            raise ValueError('File does not exist')
        return v


class StrictIPAdress(pydantic.RootModel):
    root: str = pydantic.Field(
        ..., pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?"
    )


class TimeDict(pydantic.BaseModel):
    hour: int = pydantic.Field(..., ge=0, le=23)
    minute: int = pydantic.Field(..., ge=0, le=59)
    second: int = pydantic.Field(..., ge=0, le=59)


class TimeDictPartial(pydantic.BaseModel):
    hour: Optional[int] = pydantic.Field(None, ge=0, le=23)
    minute: Optional[int] = pydantic.Field(None, ge=0, le=59)
    second: Optional[int] = pydantic.Field(None, ge=0, le=59)


class SubConfigs:
    """Class that contains TypedDicts for sections of the config file."""
    @staticmethod
    class General(pydantic.BaseModel):
        version: Literal["4.0.8"]
        seconds_per_core_interval: float = pydantic.Field(..., ge=5, le=600)
        test_mode: bool
        station_id: str
        min_sun_elevation: float = pydantic.Field(..., ge=0, le=90)

    @staticmethod
    class GeneralPartial(pydantic.BaseModel):
        """Like `SubConfigs.General`, but all fields are optional."""

        seconds_per_core_interval: Optional[float] = None
        test_mode: Optional[bool] = None
        station_id: Optional[str] = None
        min_sun_elevation: Optional[float] = None

    @staticmethod
    class Opus(pydantic.BaseModel):
        em27_ip: StrictIPAdress
        executable_path: StrictFilePath
        experiment_path: StrictFilePath
        macro_path: StrictFilePath
        username: str
        password: str

    @staticmethod
    class OpusPartial(pydantic.BaseModel):
        """Like `SubConfigs.Opus`, but all fields are optional."""

        em27_ip: Optional[StrictIPAdress] = None
        executable_path: Optional[StrictFilePath] = None
        experiment_path: Optional[StrictFilePath] = None
        macro_path: Optional[StrictFilePath] = None
        username: Optional[str] = None
        password: Optional[str] = None

    @staticmethod
    class Camtracker(pydantic.BaseModel):
        config_path: StrictFilePath
        executable_path: StrictFilePath
        learn_az_elev_path: StrictFilePath
        sun_intensity_path: StrictFilePath
        motor_offset_threshold: float = pydantic.Field(..., ge=0, le=360)

    @staticmethod
    class CamtrackerPartial(pydantic.BaseModel):
        """Like `SubConfigs.Camtracker` but all fields are optional."""

        config_path: Optional[StrictFilePath] = None
        executable_path: Optional[StrictFilePath] = None
        learn_az_elev_path: Optional[StrictFilePath] = None
        sun_intensity_path: Optional[StrictFilePath] = None
        motor_offset_threshold: Optional[float] = pydantic.Field(
            None, ge=0, le=360
        )

    @staticmethod
    class ErrorEmail(pydantic.BaseModel):
        sender_address: str
        sender_password: str
        notify_recipients: bool
        recipients: str

    @staticmethod
    class ErrorEmailPartial(pydantic.BaseModel):
        """Like `SubConfigs.ErrorEmail` but all fields are optional."""

        sender_address: Optional[str] = None
        sender_password: Optional[str] = None
        notify_recipients: Optional[bool] = None
        recipients: Optional[str] = None

    @staticmethod
    class MeasurementDecision(pydantic.BaseModel):
        mode: Literal["automatic", "manual", "cli"]
        manual_decision_result: bool
        cli_decision_result: bool

    @staticmethod
    class MeasurementDecisionPartial(pydantic.BaseModel):
        """Like `SubConfigs.MeasurementDecision` but all fields are optional."""

        mode: Optional[Literal["automatic", "manual", "cli"]] = None
        manual_decision_result: Optional[bool] = None
        cli_decision_result: Optional[bool] = None

    @staticmethod
    class MeasurementTriggers(pydantic.BaseModel):
        consider_time: bool
        consider_sun_elevation: bool
        consider_helios: bool
        start_time: TimeDict
        stop_time: TimeDict
        min_sun_elevation: float = pydantic.Field(..., ge=0, le=90)

    @staticmethod
    class MeasurementTriggersPartial(pydantic.BaseModel):
        """Like `SubConfigs.MeasurementTriggers` but all fields are optional."""

        consider_time: Optional[bool] = None
        consider_sun_elevation: Optional[bool] = None
        consider_helios: Optional[bool] = None
        start_time: Optional[TimeDictPartial] = None
        stop_time: Optional[TimeDictPartial] = None
        min_sun_elevation: Optional[float] = pydantic.Field(None, ge=0, le=90)

    @staticmethod
    class TumPlc(pydantic.BaseModel):
        ip: StrictIPAdress
        version: Literal[1, 2]
        controlled_by_user: bool

    @staticmethod
    class TumPlcPartial(pydantic.BaseModel):
        """Like `SubConfigs.TumPlc`, but all fields are optional."""

        ip: Optional[StrictIPAdress] = None
        version: Optional[Literal[1, 2]] = None
        controlled_by_user: Optional[bool] = None

    @staticmethod
    class Helios(pydantic.BaseModel):
        camera_id: int = pydantic.Field(..., ge=0, le=999999)
        evaluation_size: int = pydantic.Field(..., ge=1, le=100)
        seconds_per_interval: float = pydantic.Field(..., ge=5, le=600)
        edge_detection_threshold: float = pydantic.Field(..., ge=0, le=1)
        save_images: bool

    @staticmethod
    class HeliosPartial(pydantic.BaseModel):
        """Like `SubConfigs.Helios`, but all fields are optional."""

        camera_id: Optional[int] = pydantic.Field(None, ge=0, le=999999)
        evaluation_size: Optional[int] = pydantic.Field(None, ge=1, le=100)
        seconds_per_interval: Optional[float] = pydantic.Field(
            None, ge=5, le=600
        )
        edge_detection_threshold: Optional[float] = pydantic.Field(
            None, ge=0, le=1
        )
        save_images: Optional[bool] = None

    @staticmethod
    class Upload(pydantic.BaseModel):
        host: StrictIPAdress
        user: str
        password: str
        upload_ifgs: bool
        src_directory_ifgs: str
        dst_directory_ifgs: str
        remove_src_ifgs_after_upload: bool
        upload_helios: bool
        dst_directory_helios: str
        remove_src_helios_after_upload: bool

    @staticmethod
    class UploadPartial(pydantic.BaseModel):
        """Like `SubConfigs.Upload`, but all fields are optional."""

        host: Optional[StrictIPAdress] = None
        user: Optional[str] = None
        password: Optional[str] = None
        upload_ifgs: Optional[bool] = None
        src_directory_ifgs: Optional[str] = None
        dst_directory_ifgs: Optional[str] = None
        remove_src_ifgs_after_upload: Optional[bool] = None
        upload_helios: Optional[bool] = None
        dst_directory_helios: Optional[str] = None
        remove_src_helios_after_upload: Optional[bool] = None


class Config(pydantic.BaseModel):
    general: SubConfigs.General
    opus: SubConfigs.Opus
    camtracker: SubConfigs.Camtracker
    error_email: SubConfigs.ErrorEmail
    measurement_decision: SubConfigs.MeasurementDecision
    measurement_triggers: SubConfigs.MeasurementTriggers
    tum_plc: Optional[SubConfigs.TumPlc] = None
    helios: Optional[SubConfigs.Helios] = None
    upload: Optional[SubConfigs.Upload] = None

    @staticmethod
    def load() -> Config:
        with open(CONFIG_FILE_PATH) as f:
            return Config.model_validate_json(f.read())


class ConfigPartial(pydantic.BaseModel):
    """Like `ConfigDict`, but all fields are optional."""

    general: Optional[SubConfigs.GeneralPartial] = None
    opus: Optional[SubConfigs.OpusPartial] = None
    camtracker: Optional[SubConfigs.CamtrackerPartial] = None
    error_email: Optional[SubConfigs.ErrorEmailPartial] = None
    measurement_decision: Optional[SubConfigs.MeasurementDecisionPartial] = None
    measurement_triggers: Optional[SubConfigs.MeasurementTriggersPartial] = None
    tum_plc: Optional[SubConfigs.TumPlcPartial] = None
    helios: Optional[SubConfigs.HeliosPartial] = None
    upload: Optional[SubConfigs.UploadPartial] = None
