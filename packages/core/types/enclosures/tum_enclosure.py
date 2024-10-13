from typing import Literal, Optional
import pydantic


class StricterBaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", validate_assignment=True)


class StrictIPAdress(pydantic.RootModel[str]):
    root: str = pydantic.Field(..., pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?")


class TUMEnclosureConfig(StricterBaseModel):
    ip: StrictIPAdress
    version: Literal[1, 2]
    controlled_by_user: bool


class PartialTUMEnclosureConfig(StricterBaseModel):
    """Like `TUMEnclosureConfig`, but all fields are optional."""

    ip: Optional[StrictIPAdress] = None
    version: Optional[Literal[1, 2]] = None
    controlled_by_user: Optional[bool] = None
