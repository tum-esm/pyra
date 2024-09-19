from __future__ import annotations
import contextlib
from typing import Any, Generator, Literal, Optional
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


class StricterBaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", validate_assignment=True)


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


class TimeDict(StricterBaseModel):
    hour: int = pydantic.Field(..., ge=0, le=23)
    minute: int = pydantic.Field(..., ge=0, le=59)
    second: int = pydantic.Field(..., ge=0, le=59)

    def as_datetime_time(self) -> datetime.time:
        return datetime.time(self.hour, self.minute, self.second)


class PartialTimeDict(StricterBaseModel):
    hour: Optional[int] = pydantic.Field(None, ge=0, le=23)
    minute: Optional[int] = pydantic.Field(None, ge=0, le=59)
    second: Optional[int] = pydantic.Field(None, ge=0, le=59)


class GeneralConfig(StricterBaseModel):
    version: Literal["4.1.4"]
    seconds_per_core_interval: float = pydantic.Field(..., ge=5, le=600)
    test_mode: bool
    station_id: str
    min_sun_elevation: float = pydantic.Field(..., ge=0, le=90)


class PartialGeneralConfig(StricterBaseModel):
    """Like `GeneralConfig`, but all fields are optional."""

    version: Literal["4.1.4"] = "4.1.4"
    seconds_per_core_interval: Optional[float] = pydantic.Field(
        None, ge=5, le=600
    )
    test_mode: Optional[bool] = None
    station_id: Optional[str] = None
    min_sun_elevation: Optional[float] = pydantic.Field(None, ge=0, le=90)


class OpusConfig(StricterBaseModel):
    em27_ip: StrictIPAdress
    executable_path: StrictFilePath
    experiment_path: StrictFilePath
    macro_path: StrictFilePath
    username: str
    password: str


class PartialOpusConfig(StricterBaseModel):
    """Like `OpusConfig`, but all fields are optional."""

    em27_ip: Optional[StrictIPAdress] = None
    executable_path: Optional[StrictFilePath] = None
    experiment_path: Optional[StrictFilePath] = None
    macro_path: Optional[StrictFilePath] = None
    username: Optional[str] = None
    password: Optional[str] = None


class CamtrackerConfig(StricterBaseModel):
    config_path: StrictFilePath
    executable_path: StrictFilePath
    learn_az_elev_path: StrictFilePath
    sun_intensity_path: StrictFilePath
    motor_offset_threshold: float = pydantic.Field(..., ge=0, le=360)
    restart_if_logs_are_too_old: bool
    restart_if_cover_remains_closed: bool


class PartialCamtrackerConfig(StricterBaseModel):
    """Like `CamtrackerConfig` but all fields are optional."""

    config_path: Optional[StrictFilePath] = None
    executable_path: Optional[StrictFilePath] = None
    learn_az_elev_path: Optional[StrictFilePath] = None
    sun_intensity_path: Optional[StrictFilePath] = None
    motor_offset_threshold: Optional[float] = pydantic.Field(None, ge=0, le=360)
    restart_if_logs_are_too_old: Optional[bool] = None
    restart_if_cover_remains_closed: Optional[bool] = None


class ErrorEmailConfig(StricterBaseModel):
    smtp_host: str
    smtp_port: Literal[465, 587]
    smtp_username: str
    smtp_password: str
    sender_address: str
    notify_recipients: bool
    recipients: str


class PartialErrorEmailConfig(StricterBaseModel):
    """Like `ErrorEmailConfig` but all fields are optional."""

    smtp_host: Optional[str] = None
    smtp_port: Optional[Literal[465, 587]] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_address: Optional[str] = None
    notify_recipients: Optional[bool] = None
    recipients: Optional[str] = None


class MeasurementDecisionConfig(StricterBaseModel):
    mode: Literal["automatic", "manual", "cli"]
    manual_decision_result: bool
    cli_decision_result: bool


class PartialMeasurementDecisionConfig(StricterBaseModel):
    """Like `MeasurementDecisionConfig` but all fields are optional."""

    mode: Optional[Literal["automatic", "manual", "cli"]] = None
    manual_decision_result: Optional[bool] = None
    cli_decision_result: Optional[bool] = None


class MeasurementTriggersConfig(StricterBaseModel):
    consider_time: bool
    consider_sun_elevation: bool
    consider_helios: bool
    start_time: TimeDict
    stop_time: TimeDict
    min_sun_elevation: float = pydantic.Field(..., ge=0, le=90)


class PartialMeasurementTriggersConfig(StricterBaseModel):
    """Like `MeasurementTriggersConfig` but all fields are optional."""

    consider_time: Optional[bool] = None
    consider_sun_elevation: Optional[bool] = None
    consider_helios: Optional[bool] = None
    start_time: Optional[PartialTimeDict] = None
    stop_time: Optional[PartialTimeDict] = None
    min_sun_elevation: Optional[float] = pydantic.Field(None, ge=0, le=90)


class TumPlcConfig(StricterBaseModel):
    ip: StrictIPAdress
    version: Literal[1, 2]
    controlled_by_user: bool


class PartialTumPlcConfig(StricterBaseModel):
    """Like `TumPlcConfig`, but all fields are optional."""

    ip: Optional[StrictIPAdress] = None
    version: Optional[Literal[1, 2]] = None
    controlled_by_user: Optional[bool] = None


class HeliosConfig(StricterBaseModel):
    camera_id: int = pydantic.Field(..., ge=0, le=999999)
    evaluation_size: int = pydantic.Field(..., ge=1, le=100)
    seconds_per_interval: float = pydantic.Field(..., ge=5, le=600)
    min_seconds_between_state_changes: int = pydantic.Field(..., ge=0, le=3600)
    edge_pixel_threshold: float = pydantic.Field(..., ge=0, le=30)
    edge_color_threshold: int = pydantic.Field(..., ge=5, le=250)
    target_pixel_brightness: int = pydantic.Field(..., ge=20, le=235)
    save_images_to_archive: bool
    save_current_image: bool


class PartialHeliosConfig(StricterBaseModel):
    """Like `HeliosConfig`, but all fields are optional."""

    camera_id: Optional[int] = pydantic.Field(None, ge=0, le=999999)
    evaluation_size: Optional[int] = pydantic.Field(None, ge=1, le=100)
    seconds_per_interval: Optional[float] = pydantic.Field(None, ge=5, le=600)
    min_seconds_between_state_changes: Optional[int] = pydantic.Field(
        None, ge=0, le=3600
    )
    edge_pixel_threshold: Optional[float] = pydantic.Field(None, ge=0, le=30)
    edge_color_threshold: Optional[int] = pydantic.Field(None, ge=5, le=250)
    target_pixel_brightness: Optional[int] = pydantic.Field(None, ge=20, le=235)
    save_images_to_archive: Optional[bool] = None
    save_current_image: Optional[bool] = None


class UploadStreamConfig(StricterBaseModel):
    is_active: bool
    label: str
    variant: Literal["directories", "files"]
    dated_regex: str
    src_directory: StrictDirectoryPath
    dst_directory: str
    remove_src_after_upload: bool


class UploadConfig(StricterBaseModel):
    host: StrictIPAdress
    user: str
    password: str
    only_upload_at_night: bool
    only_upload_when_not_measuring: bool
    streams: list[UploadStreamConfig]


class PartialUploadConfig(StricterBaseModel):
    """Like `UploadConfig`, but all fields are optional."""

    host: Optional[StrictIPAdress] = None
    user: Optional[str] = None
    password: Optional[str] = None
    only_upload_at_night: Optional[bool] = None
    only_upload_when_not_measuring: Optional[bool] = None
    streams: Optional[list[UploadStreamConfig]] = None


class Config(StricterBaseModel):
    general: GeneralConfig
    opus: OpusConfig
    camtracker: CamtrackerConfig
    error_email: ErrorEmailConfig
    measurement_decision: MeasurementDecisionConfig
    measurement_triggers: MeasurementTriggersConfig
    tum_plc: Optional[TumPlcConfig] = None
    helios: Optional[HeliosConfig] = None
    upload: Optional[UploadConfig] = None

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
            else:

                def _read() -> Config:
                    with open(_CONFIG_FILE_PATH) as f:
                        return Config.model_validate_json(
                            f.read(),
                            context={
                                "ignore-path-existence": ignore_path_existence
                            },
                        )

                if with_filelock:
                    with filelock.FileLock(_CONFIG_LOCK_PATH, timeout=10):
                        return _read()
                else:
                    return _read()
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
                "Config is invalid:\n" + ',\n'.join(pretty_errors)
            ) from None

    def dump(self, with_filelock: bool = True) -> None:
        if with_filelock:
            with filelock.FileLock(_CONFIG_LOCK_PATH, timeout=10):
                with open(_CONFIG_FILE_PATH, "w") as f:
                    f.write(self.model_dump_json())
        else:
            with open(_CONFIG_FILE_PATH, "w") as f:
                f.write(self.model_dump_json())

    @staticmethod
    @contextlib.contextmanager
    @tum_esm_utils.decorators.with_filelock(
        lockfile_path=_CONFIG_LOCK_PATH, timeout=5
    )
    def update_in_context() -> Generator[Config, None, None]:
        """Update the confug file in a context manager.
        
        Example:
        
        ```python
        with Config.update_in_context() as state:
            config.somesetting = somevalue
        ```

        The file will be locked correctly, so that no other process can
        interfere with the config file and the state."""

        with open(_CONFIG_FILE_PATH) as f:
            config = Config.model_validate_json(
                f.read(),
                context={"ignore-path-existence": True},
            )

        yield config

        with open(_CONFIG_FILE_PATH, "w") as f:
            f.write(config.model_dump_json(indent=4))


class PartialConfig(StricterBaseModel):
    """Like `Config`, but all fields are optional."""

    general: Optional[PartialGeneralConfig] = None
    opus: Optional[PartialOpusConfig] = None
    camtracker: Optional[PartialCamtrackerConfig] = None
    error_email: Optional[PartialErrorEmailConfig] = None
    measurement_decision: Optional[PartialMeasurementDecisionConfig] = None
    measurement_triggers: Optional[PartialMeasurementTriggersConfig] = None
    tum_plc: Optional[PartialTumPlcConfig] = None
    helios: Optional[PartialHeliosConfig] = None
    upload: Optional[PartialUploadConfig] = None

    @staticmethod
    def load(
        config_object: str,
        ignore_path_existence: bool = False
    ) -> PartialConfig:
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
            return PartialConfig.model_validate_json(
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
