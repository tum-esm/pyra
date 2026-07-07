import pydantic
import tum_esm_utils


class KnownException(tum_esm_utils.validators.StricterBaseModel):
    error_message: str = pydantic.Field(
        ..., description="The error message raised by the exception."
    )
    long_description: str = pydantic.Field(
        ...,
        description="A proper description of the error which will also be rendered in the documentation.",
    )

    def _raise(self) -> None:
        raise Exception(self.error_message)


class KnownExceptions:
    COVER_DID_NOT_OPEN = KnownException(
        error_message="CamTracker was started but cover is closed.",
        long_description="This error might have been caused by the enclosures rain sensor being triggered long enough to cause the cover to be closed but too short for PYRA to read from rain sensor in time. This is usually self-resolving after some time since the cover either opens or the rain sensor is triggered long enough for PYRA to read it. If not resolving, the cover might be stuck/the motor might be broken and needs to be checked.",
    )
