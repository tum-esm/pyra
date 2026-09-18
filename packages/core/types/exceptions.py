import pydantic
import tum_esm_utils


class KnownException(tum_esm_utils.validators.StricterBaseModel):
    """A known exception that can be raised by the system."""

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


class KNOWN_EXCEPTIONS:
    """A collection of known exceptions that can be raised by the system."""

    COVER_DID_NOT_OPEN = KnownException(
        error_message="Enclosure cover did not open.",
        long_description=(
            "This error might have been caused by the enclosures rain sensor being triggered long enough to cause the cover to be closed but too short for PYRA to read from rain sensor in time. This is usually self-resolving after some time since the cover either opens or the rain sensor is triggered long enough for PYRA to read it. If not resolving, the cover might be stuck/the motor might be broken and needs to be checked."
        ),
    )
    COVER_DID_NOT_CLOSE = KnownException(
        error_message="Enclosure cover did not close.",
        long_description=(
            "Even though Pyra requested the enclosure cover to close, it did not reach the closed position. The cover could be blocked or the motor could have an issue. Please check the enclosure cover and motor."
        ),
    )
    STORAGE_ERROR = KnownException(
        error_message="The system disk is more than 90% full.",
        long_description=(
            "The system disk is more than 90% full. This can make the operating system unstable and might indicate that the system is producing data faster than it can upload it."
        ),
    )
    LOW_ENERGY_ERROR = KnownException(
        error_message="The system battery level is below 30%.",
        long_description="The system battery level is below 30%. Check the power supply.",
    )
    PYRA_CORE_CRASHED = KnownException(
        error_message="Pyra Core is not running and has not been shut down properly.",
        long_description='Pyra core did not shutdown with a graceful shutdown message. Normally this should only happen if the operating system forcefully killed the Pyra core process. This can also happen if the system lost power and booted back up. This error is usually raised by the Pyra UI calling "pyra-cli core is-running" to check whether a proper shutdown happened. It is automatically resolved when the Pyra core is starting again.',
    )

    # TUM enclosure

    TUM_ENCLOSURE_PLC_CONNECTION_ERROR = KnownException(
        error_message="Could not connect to TUM enclosure PLC.",
        long_description=(
            "PYRA could not establish a connection to the TUM enclosure PLC for several consecutive retries."
        ),
    )
    TUM_ENCLOSURE_RAIN_DETECTED_COVER_NOT_CLOSED = KnownException(
        error_message="Rain detected but cover is not closed.",
        long_description=("The TUM enclosure reports rain, but the cover did not close yet."),
        # different from COVER_DID_NOT_CLOSE error because now it is quite urgent to close the cover
    )
    TUM_ENCLOSURE_PLC_RESET_FAILED = KnownException(
        error_message="TUM enclosure PLC reset was required but did not work",
        long_description=(
            "The TUM enclosure PLC reported that a reset was required but triggering the reset did not resolve the issue."
        ),
    )
    TUM_ENCLOSURE_PLC_ERROR = KnownException(
        error_message="The TUM enclosure PLC responded unexpectedly.",
        long_description=(
            "Communication with the TUM enclosure PLC failed or a requested PLC value did not update as expected."
        ),
    )

    # AEMET enclosure

    AEMET_ENCLOSURE_DATALOGGER_ERROR = KnownException(
        error_message="The AEMET enclosure datalogger responded in an unexpected way.",
        long_description=(
            "Communication with the AEMET enclosure datalogger or related power plug failed, returned invalid data, or did not update as expected."
        ),
    )

    # CamTracker

    CAMTRACKER_CONFIGURATION_ERROR = KnownException(
        error_message="PYRA could not read the CamTracker configuration file.",
        long_description=(
            "PYRA could not read the CamTracker configuration file or determine the coordinates from it. Please make sure to configure the correct path for the CamTracker configuration file in the PYRA configuration."
        ),
    )

    # Helios

    HELIOS_CAMERA_ERROR = KnownException(
        error_message="Helios camera is not working as expected.",
        long_description=(
            "Helios could not initialize the camera, determine usable exposure settings, open the camera, or take images. This issues is typically raised if the camera is not responding for a while."
        ),
    )

    # OPUS / EM27

    OPUS_CONNECTION_ERROR = KnownException(
        error_message="The OPUS HTTP interface is not reachable.",
        long_description=(
            "OPUS started, but the OPUS HTTP interface did not become reachable in time. This can happen if OPUS did not start properly (normally should not happen) or if the localhost is occupied by another application. You can check whether the latter is true by opening http://localhost:8080 in a web browser and checking whether any other application is running there."
        ),
    )

    EM27_CONNECTION_ERROR = KnownException(
        error_message="The EM27 HTTP interface is not reachable.",
        long_description=("The EM27 web interface could not be reached under the configured IP."),
    )

    # Infrastructure

    LOCK_TIMEOUT_ERROR = KnownException(
        error_message="PYRA could not acquire a required lock in time.",
        long_description="Pyra uses a lock file to ensure that only one thread can access certain resources at a time. If this lock cannot be acquired in time, this error is raised. In normal operation this should not happen. If you see this error, your computer might be under heavy load so that the operating system does not allow writing to a file in time. Or your disk might be 100% occupied.",
    )
