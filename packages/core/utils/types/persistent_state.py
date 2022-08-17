from typing import Optional, TypedDict


class PersistentStateTypes:
    class Dict(TypedDict):
        active_opus_macro_id: Optional[int]
        current_exceptions: list[str]

    class PartialDict(TypedDict, total=False):
        active_opus_macro_id: Optional[int]
        current_exceptions: list[str]
