import os
import pydantic
from typing import Any, Callable, Literal, Optional, TypedDict


TimeDict = TypedDict("TimeDict", {"hour": int, "minute": int, "second": int})
TimeDictPartial = TypedDict(
    "TimeDictPartial", {"hour": int, "minute": int, "second": int}, total=False
)


class ConfigSubDicts:
    @staticmethod
    class General(TypedDict):
        version: Literal["4.0.6"]
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
        motor_offset_threshold: float

    @staticmethod
    class CamtrackerPartial(TypedDict, total=False):
        config_path: str
        executable_path: str
        learn_az_elev_path: str
        sun_intensity_path: str
        motor_offset_threshold: float

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
        start_time: TimeDict
        stop_time: TimeDict
        min_sun_elevation: float

    @staticmethod
    class MeasurementTriggersPartial(TypedDict, total=False):
        consider_time: bool
        consider_sun_elevation: bool
        consider_helios: bool
        start_time: TimeDictPartial
        stop_time: TimeDictPartial
        min_sun_elevation: float

    @staticmethod
    class TumPlc(TypedDict):
        ip: str
        version: Literal[1, 2]
        controlled_by_user: bool

    @staticmethod
    class TumPlcPartial(TypedDict, total=False):
        ip: str
        version: Literal[1, 2]
        controlled_by_user: bool

    @staticmethod
    class Helios(TypedDict):
        camera_id: int
        evaluation_size: int
        seconds_per_interval: float
        edge_detection_threshold: float
        save_images: bool

    @staticmethod
    class HeliosPartial(TypedDict, total=False):
        camera_id: int
        evaluation_size: int
        seconds_per_interval: float
        edge_detection_threshold: float
        save_images: bool

    @staticmethod
    class Upload(TypedDict):
        host: str
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
    class UploadPartial(TypedDict, total=False):
        host: str
        user: str
        password: str
        upload_ifgs: bool
        src_directory_ifgs: str
        dst_directory_ifgs: str
        remove_src_ifgs_after_upload: bool
        upload_helios: bool
        dst_directory_helios: str
        remove_src_helios_after_upload: bool


class ConfigDict(TypedDict):
    general: ConfigSubDicts.General
    opus: ConfigSubDicts.Opus
    camtracker: ConfigSubDicts.Camtracker
    error_email: ConfigSubDicts.ErrorEmail
    measurement_decision: ConfigSubDicts.MeasurementDecision
    measurement_triggers: ConfigSubDicts.MeasurementTriggers
    tum_plc: Optional[ConfigSubDicts.TumPlc]
    helios: Optional[ConfigSubDicts.Helios]
    upload: Optional[ConfigSubDicts.Upload]


class ConfigDictPartial(TypedDict, total=False):
    general: ConfigSubDicts.GeneralPartial
    opus: ConfigSubDicts.OpusPartial
    camtracker: ConfigSubDicts.CamtrackerPartial
    error_email: ConfigSubDicts.ErrorEmailPartial
    measurement_decision: ConfigSubDicts.MeasurementDecisionPartial
    measurement_triggers: ConfigSubDicts.MeasurementTriggersPartial
    tum_plc: Optional[ConfigSubDicts.TumPlcPartial]
    helios: Optional[ConfigSubDicts.HeliosPartial]
    upload: Optional[ConfigSubDicts.UploadPartial]


class ValidationError(Exception):
    """
    Will be raised in any custom checks on config dicts
    have failed: file-existence, ip-format, min/max-range
    """


def validate_config_dict(o: Any, partial: bool = False, skip_filepaths: bool = False) -> None:
    """
    Check, whether a given object is a correct ConfigDict
    Raises a pydantic.ValidationError if the object is invalid.

    This should always be used when loading the object from a
    JSON file!
    """
    try:
        if partial:
            _ValidationModel(partial=o)
        else:
            _ValidationModel(regular=o)
    except pydantic.ValidationError as e:
        pretty_error_messages = []
        for error in e.errors():
            fields = [str(f) for f in error["loc"][1:] if f not in ["__root__"]]
            pretty_error_messages.append(f"{'.'.join(fields)} -> {error['msg']}")
        raise ValidationError(f"config is invalid: {', '.join(pretty_error_messages)}")

    new_object: ConfigDict = o

    def get_nested_dict_property(property_path: str) -> Any:
        prop = new_object
        for key in property_path.split("."):
            prop = prop[key]  # type: ignore
        return prop

    def assert_min_max(property_path: str, min_value: float, max_value: float) -> None:
        prop: float = get_nested_dict_property(property_path)
        error_message = f"config.{property_path} must be in range [{min_value}, {max_value}]"
        assert prop >= min_value, error_message
        assert prop <= max_value, error_message

    def assert_file_path(property_path: str) -> None:
        prop: str = get_nested_dict_property(property_path)
        if not skip_filepaths:
            assert os.path.isfile(prop), f"config.{property_path} is not a file"

    def assert_ip_address(property_path: str) -> None:
        prop: str = get_nested_dict_property(property_path)
        error_message = f"config.{property_path} is not a valid ip address"
        values: list[str] = prop.split(".")
        assert len(values) == 4, error_message
        assert all([x.isnumeric() for x in values]), error_message
        assert all([0 <= int(x) <= 255 for x in values]), error_message

    assertions: list[Callable[[], None]] = [
        lambda: assert_min_max("general.seconds_per_core_interval", 5, 600),
        lambda: assert_min_max("general.min_sun_elevation", 0, 90),
        lambda: assert_ip_address("opus.em27_ip"),
        lambda: assert_file_path("opus.executable_path"),
        lambda: assert_file_path("opus.experiment_path"),
        lambda: assert_file_path("opus.macro_path"),
        lambda: assert_file_path("camtracker.config_path"),
        lambda: assert_file_path("camtracker.executable_path"),
        lambda: assert_file_path("camtracker.learn_az_elev_path"),
        lambda: assert_file_path("camtracker.sun_intensity_path"),
        lambda: assert_min_max("camtracker.motor_offset_threshold", -360, 360),
        lambda: assert_min_max("measurement_triggers.min_sun_elevation", 0, 90),
        lambda: assert_min_max("measurement_triggers.start_time.hour", 0, 23),
        lambda: assert_min_max("measurement_triggers.stop_time.hour", 0, 23),
        lambda: assert_min_max("measurement_triggers.start_time.minute", 0, 59),
        lambda: assert_min_max("measurement_triggers.stop_time.minute", 0, 59),
        lambda: assert_min_max("measurement_triggers.start_time.second", 0, 59),
        lambda: assert_min_max("measurement_triggers.stop_time.second", 0, 59),
        lambda: assert_ip_address("tum_plc.ip"),
        lambda: assert_min_max("helios.camera_id", 0, 999999),
        lambda: assert_min_max("helios.evaluation_size", 1, 100),
        lambda: assert_min_max("helios.seconds_per_interval", 5, 600),
        lambda: assert_min_max("helios.edge_detection_threshold", 0, 1),
        lambda: assert_ip_address("upload.host"),
    ]

    # this does not check for a valid upload.src_directory_ifgs path
    # since the thread itself will check for this

    pretty_error_messages = []

    for assertion in assertions:
        try:
            assertion()
        except AssertionError as a:
            pretty_error_messages.append(a.args[0])
        except (TypeError, KeyError):
            # Will be ignored because the structure is already
            # validated. Occurs when property is missing
            pass

    if len(pretty_error_messages) > 0:
        raise ValidationError(f"config is invalid: {', '.join(pretty_error_messages)}")


class _ValidationModel(pydantic.BaseModel):
    regular: Optional[ConfigDict]
    partial: Optional[ConfigDictPartial]

    class Config:
        extra = "forbid"
