import pydantic
from typing import Optional


class PersistentState(pydantic.BaseModel):
    """A pydantic model for the persistent state file."""

    active_opus_macro_id: int = -1
    current_exceptions: list[str] = []


class PersistentStatePartial(pydantic.BaseModel):
    """A pydantic model for the persistent state file."""

    active_opus_macro_id: Optional[int] = None
    current_exceptions: Optional[list[str]] = None
