from __future__ import annotations
from typing import Optional
import datetime
import json
import os
import pydantic
from packages.core import types

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))


def _date_to_filepath(date: datetime.date) -> str:
    return os.path.join(_PROJECT_DIR, "logs", "activity", f"activity-{date}.json")


def _load_current_activity_history() -> types.ActivityHistory:
    today = datetime.date.today()

    try:
        with open(_date_to_filepath(today), "r") as f:
            return types.ActivityHistory(datapoints=json.load(f), date=today)
    except (
        json.JSONDecodeError,
        FileNotFoundError,
        pydantic.ValidationError,
    ):
        return types.ActivityHistory(date=today)


class ActivityHistoryInterface:
    """Logging the system activity every minute to 
    `logs/activity/activity-YYYY-MM-DD.json` to plot
    it in the UI."""

    current_activity_history: types.ActivityHistory = _load_current_activity_history()
    last_write_time: datetime.datetime = datetime.datetime(1970, 1, 1)

    @staticmethod
    def add_datapoint(
        is_measuring: Optional[bool] = None,
        has_errors: Optional[bool] = None,
        is_uploading: Optional[bool] = None,
        camtracker_startups: Optional[int] = None,
        opus_startups: Optional[int] = None,
        cli_calls: Optional[int] = None,
    ) -> None:
        """Add a new activity datapoint. When this function is called
        multiple times in the same minute, the datapoints are aggregated
        into one datapoint per minute."""

        current_local_datetime = datetime.datetime.now()

        if (
            ActivityHistoryInterface.current_activity_history.date != current_local_datetime.date()
        ):
            ActivityHistoryInterface.dump_current_activity_history()
            ActivityHistoryInterface.current_activity_history = types.ActivityHistory(
                date=current_local_datetime.date()
            )

        current_history = ActivityHistoryInterface.current_activity_history
        new_history = current_history.__deepcopy__()

        # determining if the last datapoint is from the same minute
        # if so, we update it, otherwise we create a new one
        last_activity_datapoint: Optional[types.ActivityDatapoint] = None
        if len(new_history.datapoints.root) > 0:
            last_activity_datapoint = new_history.datapoints.root[-1]

        if last_activity_datapoint is not None:
            if (
                last_activity_datapoint.local_time.strftime("%H:%M")
                != current_local_datetime.strftime("%H:%M")
            ):
                last_activity_datapoint = None

        # creating a new datapoint if none exist for the current minute
        current_activity_datapoint = last_activity_datapoint
        if current_activity_datapoint is None:
            current_activity_datapoint = types.ActivityDatapoint(
                local_time=datetime.time(
                    hour=current_local_datetime.hour,
                    minute=current_local_datetime.minute,
                ),
            )
            new_history.datapoints.root.append(current_activity_datapoint)

        # do not downgrade a True to a False value
        # only upgrade a False to a True value
        if is_measuring is not None:
            current_activity_datapoint.is_measuring |= is_measuring
        if has_errors is not None:
            current_activity_datapoint.has_errors |= has_errors
        if is_uploading is not None:
            current_activity_datapoint.is_uploading |= is_uploading
        if camtracker_startups is not None:
            current_activity_datapoint.camtracker_startups += camtracker_startups
        if opus_startups is not None:
            current_activity_datapoint.opus_startups += opus_startups
        if cli_calls is not None:
            current_activity_datapoint.cli_calls += cli_calls

        ActivityHistoryInterface.current_activity_history = new_history

        # writing the activity history to the file if
        #   * first datapoint of the instance running
        #   * last write was at least 5 minutes ago
        if ((last_activity_datapoint is None) or
            ((ActivityHistoryInterface.last_write_time - current_local_datetime).total_seconds()
             >= 300)):
            ActivityHistoryInterface.dump_current_activity_history()

    @staticmethod
    def dump_current_activity_history() -> None:
        activity_history = ActivityHistoryInterface.current_activity_history
        assert activity_history is not None
        with open(_date_to_filepath(activity_history.date), "w") as f:
            f.write(activity_history.datapoints.model_dump_json())

        ActivityHistoryInterface.last_write_time = datetime.datetime.now()
