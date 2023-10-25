from __future__ import annotations
from typing import Any, Literal, Optional
import datetime
import os
import filelock
import pydantic
import tum_esm_utils

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(
    __file__, current_depth=4
)
_CONFIG_FILE_PATH = os.path.join(_PROJECT_DIR, "config", "config.json")
_CONFIG_LOCK_PATH = os.path.join(_PROJECT_DIR, "config", ".config.lock")


class StrictFilePath(pydantic.RootModel[str]):
    root: str

    @pydantic.field_validator('root')
    @classmethod
    def path_should_exist(cls, v: str, info: pydantic.ValidationInfo) -> str:
        ignore_path_existence = (
            info.context.get('ignore-path-existence') == True
        ) if isinstance(info.context, dict) else False
        if (not ignore_path_existence) and (not os.path.isfile(v)):
            raise ValueError('File does not exist')
        return v


class StrictDirectoryPath(pydantic.RootModel[str]):
    root: str

    @pydantic.field_validator('root')
    @classmethod
    def path_should_exist(cls, v: str, info: pydantic.ValidationInfo) -> str:
        ignore_path_existence = (
            info.context.get('ignore-path-existence') == True
        ) if isinstance(info.context, dict) else False
        if (not ignore_path_existence) and (not os.path.isdir(v)):
            raise ValueError('Directory does not exist')
        return v


class StrictIPAdress(pydantic.RootModel[str]):
    root: str = pydantic.Field(
        ..., pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?"
    )


class TimeDict(pydantic.BaseModel):
    hour: int = pydantic.Field(..., ge=0, le=23)
    minute: int = pydantic.Field(..., ge=0, le=59)
    second: int = pydantic.Field(..., ge=0, le=59)

    def as_datettime_time(self) -> datetime.time:
        return datetime.time(self.hour, self.minute, self.second)


class TimeDictPartial(pydantic.BaseModel):
    hour: Optional[int] = pydantic.Field(None, ge=0, le=23)
    minute: Optional[int] = pydantic.Field(None, ge=0, le=59)
    second: Optional[int] = pydantic.Field(None, ge=0, le=59)


class SubConfigGeneral(pydantic.BaseModel):
    version: Literal["4.1.0"]
    seconds_per_core_interval: float = pydantic.Field(..., ge=5, le=600)
    test_mode: bool
    station_id: str
    min_sun_elevation: float = pydantic.Field(..., ge=0, le=90)


class SubConfigGeneralPartial(pydantic.BaseModel):
    """Like `SubConfigGeneral`, but all fields are optional."""

    seconds_per_core_interval: Optional[float] = pydantic.Field(
        None, ge=5, le=600
    )
    test_mode: Optional[bool] = None
    station_id: Optional[str] = None
    min_sun_elevation: Optional[float] = pydantic.Field(None, ge=0, le=90)


class SubConfigOpus(pydantic.BaseModel):
    em27_ip: StrictIPAdress
    executable_path: StrictFilePath
    experiment_path: StrictFilePath
    macro_path: StrictFilePath
    username: str
    password: str


class SubConfigOpusPartial(pydantic.BaseModel):
    """Like `SubConfigOpus`, but all fields are optional."""

    em27_ip: Optional[StrictIPAdress] = None
    executable_path: Optional[StrictFilePath] = None
    experiment_path: Optional[StrictFilePath] = None
    macro_path: Optional[StrictFilePath] = None
    username: Optional[str] = None
    password: Optional[str] = None


class SubConfigCamtracker(pydantic.BaseModel):
    config_path: StrictFilePath
    executable_path: StrictFilePath
    learn_az_elev_path: StrictFilePath
    sun_intensity_path: StrictFilePath
    motor_offset_threshold: float = pydantic.Field(..., ge=0, le=360)
    restart_if_logs_are_too_old: bool


class SubConfigCamtrackerPartial(pydantic.BaseModel):
    """Like `SubConfigCamtracker` but all fields are optional."""

    config_path: Optional[StrictFilePath] = None
    executable_path: Optional[StrictFilePath] = None
    learn_az_elev_path: Optional[StrictFilePath] = None
    sun_intensity_path: Optional[StrictFilePath] = None
    motor_offset_threshold: Optional[float] = pydantic.Field(None, ge=0, le=360)
    restart_if_logs_are_too_old: Optional[bool] = None


class SubConfigErrorEmail(pydantic.BaseModel):
    smtp_host: str
    smtp_port: Literal[465, 587]
    smtp_username: str
    smtp_password: str
    sender_address: str
    notify_recipients: bool
    recipients: str


class SubConfigErrorEmailPartial(pydantic.BaseModel):
    """Like `SubConfigErrorEmail` but all fields are optional."""

    smtp_host: Optional[str] = None
    smtp_port: Optional[Literal[465, 587]] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_address: Optional[str] = None
    notify_recipients: Optional[bool] = None
    recipients: Optional[str] = None


class SubConfigMeasurementDecision(pydantic.BaseModel):
    mode: Literal["automatic", "manual", "cli"]
    manual_decision_result: bool
    cli_decision_result: bool


class SubConfigMeasurementDecisionPartial(pydantic.BaseModel):
    """Like `SubConfigMeasurementDecision` but all fields are optional."""

    mode: Optional[Literal["automatic", "manual", "cli"]] = None
    manual_decision_result: Optional[bool] = None
    cli_decision_result: Optional[bool] = None


class SubConfigMeasurementTriggers(pydantic.BaseModel):
    consider_time: bool
    consider_sun_elevation: bool
    consider_helios: bool
    start_time: TimeDict
    stop_time: TimeDict
    min_sun_elevation: float = pydantic.Field(..., ge=0, le=90)


class SubConfigMeasurementTriggersPartial(pydantic.BaseModel):
    """Like `SubConfigMeasurementTriggers` but all fields are optional."""

    consider_time: Optional[bool] = None
    consider_sun_elevation: Optional[bool] = None
    consider_helios: Optional[bool] = None
    start_time: Optional[TimeDictPartial] = None
    stop_time: Optional[TimeDictPartial] = None
    min_sun_elevation: Optional[float] = pydantic.Field(None, ge=0, le=90)


class SubConfigTumPlc(pydantic.BaseModel):
    ip: StrictIPAdress
    version: Literal[1, 2]
    controlled_by_user: bool


class SubConfigTumPlcPartial(pydantic.BaseModel):
    """Like `SubConfigTumPlc`, but all fields are optional."""

    ip: Optional[StrictIPAdress] = None
    version: Optional[Literal[1, 2]] = None
    controlled_by_user: Optional[bool] = None


class SubConfigHelios(pydantic.BaseModel):
    camera_id: int = pydantic.Field(..., ge=0, le=999999)
    evaluation_size: int = pydantic.Field(..., ge=1, le=100)
    seconds_per_interval: float = pydantic.Field(..., ge=5, le=600)
    edge_detection_threshold: float = pydantic.Field(..., ge=0, le=1)
    save_images: bool


class SubConfigHeliosPartial(pydantic.BaseModel):
    """Like `SubConfigHelios`, but all fields are optional."""

    camera_id: Optional[int] = pydantic.Field(None, ge=0, le=999999)
    evaluation_size: Optional[int] = pydantic.Field(None, ge=1, le=100)
    seconds_per_interval: Optional[float] = pydantic.Field(None, ge=5, le=600)
    edge_detection_threshold: Optional[float] = pydantic.Field(None, ge=0, le=1)
    save_images: Optional[bool] = None


class SubConfigUpload(pydantic.BaseModel):
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


class SubConfigUploadPartial(pydantic.BaseModel):
    """Like `SubConfigUpload`, but all fields are optional."""

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
    general: SubConfigGeneral
    opus: SubConfigOpus
    camtracker: SubConfigCamtracker
    error_email: SubConfigErrorEmail
    measurement_decision: SubConfigMeasurementDecision
    measurement_triggers: SubConfigMeasurementTriggers
    tum_plc: Optional[SubConfigTumPlc] = None
    helios: Optional[SubConfigHelios] = None
    upload: Optional[SubConfigUpload] = None

    @staticmethod
    def load(
        config_object: Optional[str | dict[Any, Any]] = None,
        with_filelock: bool = True,
        ignore_path_existence: bool = False
    ) -> Config:
        """Load the config file.
        
        Args:
            config_object:          If provided, the config file will be ignored and
                                    the provided content will be used instead. Defaults
                                    to None.
            with_filelock:          If True, the config file will be locked
                                    during loading. Defaults to True.
            ignore_path_existence:  If True, the existence of the file and directory
                                    paths used in the whole config file will not be
                                    checked. Defaults to False.
        
        Returns:  The loaded config object.
        
        Raises:
            ValueError:  If the config file is invalid.
        """

        try:

            if config_object is not None:
                if isinstance(config_object, dict):
                    return Config.model_validate(
                        config_object,
                        context={
                            "ignore-path-existence": ignore_path_existence
                        },
                    )
                else:
                    return Config.model_validate_json(
                        config_object,
                        context={
                            "ignore-path-existence": ignore_path_existence
                        },
                    )

            if with_filelock:
                with filelock.FileLock(_CONFIG_LOCK_PATH, timeout=10):
                    with open(_CONFIG_FILE_PATH) as f:
                        return Config.model_validate_json(
                            f.read(),
                            context={
                                "ignore-path-existence": ignore_path_existence
                            },
                        )
            else:
                with open(_CONFIG_FILE_PATH) as f:
                    return Config.model_validate_json(
                        f.read(),
                        context={
                            "ignore-path-existence": ignore_path_existence
                        },
                    )

        except pydantic.ValidationError as e:
            pretty_errors: list[str] = []
            for er in e.errors():
                location = ".".join([str(err) for err in er["loc"]])
                message = er["msg"]
                value = er["input"]
                pretty_errors.append(
                    f"Error in {location}: {message} (value: {value})"
                )

            # the "from None" suppresses the pydantic exception
            raise ValueError(
                f"Config is invalid: {','.join(pretty_errors)}"
            ) from None

    def dump(self, with_filelock: bool = True) -> None:
        if with_filelock:
            with filelock.FileLock(_CONFIG_LOCK_PATH, timeout=10):
                with open(_CONFIG_FILE_PATH, "w") as f:
                    f.write(self.model_dump_json())
        else:
            with open(_CONFIG_FILE_PATH, "w") as f:
                f.write(self.model_dump_json())


class ConfigPartial(pydantic.BaseModel):
    """Like `ConfigDict`, but all fields are optional."""

    general: Optional[SubConfigGeneralPartial] = None
    opus: Optional[SubConfigOpusPartial] = None
    camtracker: Optional[SubConfigCamtrackerPartial] = None
    error_email: Optional[SubConfigErrorEmailPartial] = None
    measurement_decision: Optional[SubConfigMeasurementDecisionPartial] = None
    measurement_triggers: Optional[SubConfigMeasurementTriggersPartial] = None
    tum_plc: Optional[SubConfigTumPlcPartial] = None
    helios: Optional[SubConfigHeliosPartial] = None
    upload: Optional[SubConfigUploadPartial] = None

    @staticmethod
    def load(
        config_object: str,
        ignore_path_existence: bool = False
    ) -> ConfigPartial:
        """Load a partial config file.
        
        Args:
            config_object:          JSON string containing a partial config.
            ignore_path_existence:  If True, the existence of the file and directory
                                    paths used in the whole config file will not be
                                    checked. Defaults to False.
        
        Returns:  The loaded partial config object.
        
        Raises:
            ValueError:  If the config file is invalid.
        """

        try:
            return ConfigPartial.model_validate_json(
                config_object,
                context={"ignore-path-existence": ignore_path_existence},
            )
        except pydantic.ValidationError as e:
            pretty_errors: list[str] = []
            for er in e.errors():
                location = ".".join([str(err) for err in er["loc"]])
                message = er["msg"]
                value = er["input"]
                pretty_errors.append(
                    f"Error in {location}: {message} (value: {value})"
                )

            # the "from None" suppresses the pydantic exception
            raise ValueError(
                f"ConfigPartial is invalid: {','.join(pretty_errors)}"
            ) from None
