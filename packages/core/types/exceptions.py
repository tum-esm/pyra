import pydantic
import tum_esm_utils


class KnownException(tum_esm_utils.validators.StricterBaseModel):
    error_message: str = pydantic.Field(
        ..., description="The error message raised by the exception."
    )
    long_description: str = pydantic.Field(
        ...,
        description=(
            "A proper description of the error which will also be rendered in the documentation."
        ),
    )
    min_patience: float = pydantic.Field(
        default=0,
        description=(
            "The user-configured patience value is the time in sectonds after which to send an email notification for this exception if it was not resolved before. This is used to avoid spamming the user with emails for the same exception over and over again. This value is the minimum time allowed for the user-configured patience value for this exception."
        ),
    )
    max_patience: float = pydantic.Field(
        default=3600,
        description=(
            "The user-configured patience value is the time in sectonds after which to send an email notification for this exception if it was not resolved before. This is used to avoid spamming the user with emails for the same exception over and over again. This value is the maximum time allowed for the user-configured patience value for this exception."
        ),
    )


class KnownExceptions:
    COVER_DID_NOT_OPEN = KnownException(
        error_message="Camtracker was started but cover is closed.",
        long_description=(
            "This error might have been caused by the enclosures rain sensor being triggered long enough to cause the cover to be closed but too short for PYRA to read from rain sensor in time. This is usually self-resolving after some time since the cover either opens or the rain sensor is triggered long enough for PYRA to read it. If not resolving, the cover might be stuck/the motor might be broken and needs to be checked."
        ),
    )
    STORAGE_ERROR = KnownException(
        error_message="The system disk is more than 90% full.",
        long_description=(
            "The system disk is more than 90% full. This can make the operating system unstable."
        ),
    )
    LOW_ENERGY_ERROR = KnownException(
        error_message="The system battery level is below 30%.",
        long_description="The system battery level is below 30%. Check the power supply.",
    )
    PYRA_CORE_CRASHED = KnownException(
        error_message="Pyra Core is not running and has not been shut down properly.",
        long_description='Pyra core did not shutdown with a graceful shutdown message. Normally this should only happen if the operating system forcefully killed the Pyra core process. This can also happen if the system lost power and booted back up. This error is usually raised by the Pyra UI calling "pyra-cli core is-running" to check whether a proper shutdown happened.',
    )

    )
