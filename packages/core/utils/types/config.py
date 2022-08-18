from typing import Any, Literal, Optional, TypedDict
import pydantic


_TimeDict = TypedDict("start_time", {"hour": int, "minute": int, "second": int})
_TimeDictPartial = TypedDict(
    "start_time", {"hour": int, "minute": int, "second": int}, total=False
)


class _ConfigSubDicts:
    @staticmethod
    class General(TypedDict):
        seconds_per_core_interval: float
        test_mode: bool
        station_id: str
        min_sun_elevation: float

    @staticmethod
    class GeneralPartial(TypedDict, total=False):
        seconds_per_core_interval: float
        test_mode: bool
        station_id: str
        min_sun_elevation: float

    @staticmethod
    class Opus(TypedDict):
        em27_ip: str
        executable_path: str
        experiment_path: str
        macro_path: str
        username: str
        password: str

    @staticmethod
    class OpusPartial(TypedDict, total=False):
        em27_ip: str
        executable_path: str
        experiment_path: str
        macro_path: str
        username: str
        password: str

    @staticmethod
    class Camtracker(TypedDict):
        config_path: str
        executable_path: str
        learn_az_elev_path: str
        sun_intensity_path: str
        motor_offset_threshold: str

    @staticmethod
    class CamtrackerPartial(TypedDict, total=False):
        config_path: str
        executable_path: str
        learn_az_elev_path: str
        sun_intensity_path: str
        motor_offset_threshold: str

    @staticmethod
    class ErrorEmail(TypedDict):
        sender_address: str
        sender_password: str
        notify_recipients: bool
        recipients: str

    @staticmethod
    class ErrorEmailPartial(TypedDict, total=False):
        sender_address: str
        sender_password: str
        notify_recipients: bool
        recipients: str

    @staticmethod
    class MeasurementDecision(TypedDict):
        mode: Literal["automatic", "manual", "cli"]
        manual_decision_result: bool
        cli_decision_result: bool

    @staticmethod
    class MeasurementDecisionPartial(TypedDict, total=False):
        mode: Literal["automatic", "manual", "cli"]
        manual_decision_result: bool
        cli_decision_result: bool

    @staticmethod
    class MeasurementTriggers(TypedDict):
        consider_time: bool
        consider_sun_elevation: bool
        consider_helios: bool
        start_time: _TimeDict
        stop_time: _TimeDict
        min_sun_elevation: float

    @staticmethod
    class MeasurementTriggersPartial(TypedDict, total=False):
        consider_time: bool
        consider_sun_elevation: bool
        consider_helios: bool
        start_time: _TimeDict
        stop_time: _TimeDict
        min_sun_elevation: float

    @staticmethod
    class TumPlc(TypedDict):
        ip: str
        version: Literal[0, 1]
        controlled_by_user: bool

    @staticmethod
    class TumPlcPartial(TypedDict, total=False):
        ip: str
        version: Literal[0, 1]
        controlled_by_user: bool

    @staticmethod
    class Helios(TypedDict):
        camera_id: int
        evaluation_size: int
        seconds_per_interval: float
        measurement_threshold: float
        save_images: bool

    @staticmethod
    class HeliosPartial(TypedDict, total=False):
        camera_id: int
        evaluation_size: int
        seconds_per_interval: float
        measurement_threshold: float
        save_images: bool

    @staticmethod
    class Upload(TypedDict):
        is_active: bool
        host: str
        user: str
        password: str
        src_directory: str
        dst_directory: str
        remove_src_after_upload: bool

    @staticmethod
    class UploadPartial(TypedDict, total=False):
        is_active: bool
        host: str
        user: str
        password: str
        src_directory: str
        dst_directory: str
        remove_src_after_upload: bool


class ConfigDict(TypedDict):
    general: _ConfigSubDicts.General
    opus: _ConfigSubDicts.Opus
    camtracker: _ConfigSubDicts.Camtracker
    error_email: _ConfigSubDicts.ErrorEmail
    measurement_decision: _ConfigSubDicts.MeasurementDecision
    measurement_triggers: _ConfigSubDicts.MeasurementTriggers
    tum_plc: Optional[_ConfigSubDicts.TumPlc]
    helios: Optional[_ConfigSubDicts.Helios]
    upload: Optional[_ConfigSubDicts.Upload]


class ConfigDictPartial(TypedDict, total=False):
    general: _ConfigSubDicts.GeneralPartial
    opus: _ConfigSubDicts.OpusPartial
    camtracker: _ConfigSubDicts.CamtrackerPartial
    error_email: _ConfigSubDicts.ErrorEmailPartial
    measurement_decision: _ConfigSubDicts.MeasurementDecisionPartial
    measurement_triggers: _ConfigSubDicts.MeasurementTriggersPartial
    tum_plc: Optional[_ConfigSubDicts.TumPlcPartial]
    helios: Optional[_ConfigSubDicts.HeliosPartial]
    upload: Optional[_ConfigSubDicts.UploadPartial]


def validate_config_dict(o: Any, partial: bool = False) -> None:
    """
    Check, whether a given object is a correct ConfigDict
    Raises a pydantic.ValidationError if the object is invalid.

    This should always be used when loading the object from a
    JSON file!
    """
    if partial:
        _ValidationModel(partial=o)
    else:
        _ValidationModel(regular=o)


class _ValidationModel(pydantic.BaseModel):
    regular: Optional[ConfigDict]
    partial: Optional[ConfigDictPartial]
