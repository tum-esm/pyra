from __future__ import annotations
import datetime
import json
import os
from typing import Optional
import pydantic

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))


class ActivityDatapoint(pydantic.BaseModel):
    """A datapoint of the activity history."""

    local_time: str
    measuring: bool = False
    errors: bool = False
    uploading: bool = False


class ActivityDatapointList(pydantic.BaseModel):
    """A datapoint of the activity history."""

    __root__: list[ActivityDatapoint]


example = {
    "localTime": "12:00", "measuring": True, "errors": False, "uploading": False
}


class ActivityHistory(pydantic.BaseModel):
    """A datapoint of the activity history."""

    datapoints: ActivityDatapointList = ActivityDatapointList()
    date: datetime.date


class ActivityHistoryInterface:
    """Logging the system activity every minute to `logs/activity/activity-YYYY-MM-DD.json` to plot it in the UI."""

    current_activity_history: Optional[ActivityHistory] = None
    last_write_time: Optional[datetime.datetime] = None

    @staticmethod
    def add_datapoint(
        measuring: Optional[bool] = None,
        errors: Optional[bool] = None,
        uploading: Optional[bool] = None,
    ) -> None:
        """Add a new activity datapoint"""

        current_local_datetime = datetime.datetime.now()

        new_history: ActivityHistory = ActivityHistoryInterface.load_activity_history(
            date=current_local_datetime.date()
        )

        # determining if the last datapoint is from the same minute
        # if so, we update it, otherwise we create a new one
        last_activity_datapoint: Optional[ActivityDatapoint] = None
        if len(new_history.datapoints.__root__) > 0:
            last_activity_datapoint = new_history.datapoints.__root__[-1]
        if last_activity_datapoint is not None:
            last_local_time = datetime.datetime.strptime(
                last_activity_datapoint.local_time, "%H:%M"
            ).time()
            if not (last_local_time == current_local_datetime.time()):
                last_activity_datapoint = None

        # creating a new datapoint or updating the last one
        if last_activity_datapoint is None:
            new_history.datapoints.__root__.append(
                ActivityDatapoint(
                    local_time=current_local_datetime.strftime("%H:%M"),
                    measuring=measuring,
                    errors=errors,
                    uploading=uploading,
                )
            )
        else:
            # do not downgrade a True to a False value
            # only upgrade a False to a True value
            if measuring is not None:
                last_activity_datapoint.measuring &= measuring
            if errors is not None:
                last_activity_datapoint.errors &= errors
            if uploading is not None:
                last_activity_datapoint.uploading &= uploading

        # writing the activity history to the file if
        # * first datapoint of the instance running
        # * it is a new day
        # * last write was at least 5 minutes ago
        dump_activity_history = (
            (ActivityHistoryInterface.current_activity_history is None) or
            (ActivityHistoryInterface.last_write_time is None) or (
                ActivityHistoryInterface.current_activity_history.date
                != new_history.date
            ) or ((
                ActivityHistoryInterface.last_write_time -
                current_local_datetime
            ).total_seconds() >= 300)
        )

        ActivityHistoryInterface.current_activity_history = new_history
        if dump_activity_history:
            ActivityHistoryInterface.dump_activity_history()

    @staticmethod
    def load_activity_history(date: datetime.date) -> ActivityHistory:
        if ActivityHistoryInterface.current_activity_history is not None:
            if ActivityHistoryInterface.current_activity_history.date == date:
                return ActivityHistoryInterface.current_activity_history

        with open(ActivityHistoryInterface.__date_to_filepath(date), "w") as f:
            try:
                return ActivityHistory(datapoints=json.load(f), date=date)
            except (
                json.JSONDecodeError,
                FileNotFoundError,
                pydantic.ValidationError,
            ):
                return ActivityHistory(date=date)

    # TODO: dump activity history when shutting down
    # TODO: add information about CLI commands to activity history
    # TODO: add information about CamTracker restarts to activity history

    @staticmethod
    def dump_activity_history() -> None:
        activity_history = ActivityHistoryInterface.current_activity_history
        assert activity_history is not None
        with open(
            ActivityHistoryInterface.__date_to_filepath(activity_history.date),
            "w"
        ) as f:
            f.write(activity_history.datapoints.model_dump_json())

    @staticmethod
    def __date_to_filepath(date: datetime.date) -> str:
        return os.path.join(
            _PROJECT_DIR, "logs", "activity", f"activity-{date}.json"
        )
