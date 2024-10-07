from __future__ import annotations
import datetime
import pydantic


class ActivityDatapoint(pydantic.BaseModel):
    """A datapoint of the activity history."""

    local_time: datetime.time
    is_measuring: bool = False
    has_errors: bool = False
    is_uploading: bool = False
    camtracker_startups: int = 0
    opus_startups: int = 0
    cli_calls: int = 0


class ActivityDatapointList(pydantic.RootModel[list[ActivityDatapoint]]):
    """A datapoint of the activity history."""

    root: list[ActivityDatapoint]


example = {"localTime": "12:00", "measuring": True, "errors": False, "uploading": False}


class ActivityHistory(pydantic.BaseModel):
    """A datapoint of the activity history."""

    datapoints: ActivityDatapointList = ActivityDatapointList(root=[])
    date: datetime.date
