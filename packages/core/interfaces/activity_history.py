from __future__ import annotations
import datetime
import os
import time
from typing import Optional
import tum_esm_utils
from packages.core import types, utils

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)
_MINUTES_BETWEEN_DUMPS = 2


class ActivityHistoryInterface:
    def __init__(self, logger: utils.Logger) -> None:
        self.last_dump_time = time.time()
        self.logger = logger
        self.activity_history: Optional[types.ActivityHistory] = None

    def get(self) -> tuple[types.ActivityHistory, int]:
        """Return the current activity history and the current minute index.

        Creates a new file if it doesn't exist yet."""

        now = datetime.datetime.now()
        minute_index = now.hour * 60 + now.minute

        # if loaded, return if same date otherwise dump and unload
        if self.activity_history is not None:
            if now.date() == self.activity_history.date:
                return self.activity_history, minute_index
            else:
                ActivityHistoryInterface._dump(self.activity_history)
                self.activity_history = None

        # -> a new file has to be loaded/initialized

        path = ActivityHistoryInterface._filepath(now.date())
        if os.path.exists(path):
            try:
                return types.ActivityHistory.model_validate_json(
                    tum_esm_utils.files.load_file(path)
                ), minute_index
            except Exception as e:
                self.logger.warning(f"Could not load existing activity history file at {path}: {e}")

        self.logger.info(f"Creating new activity history file at {path}")
        new_ah = types.ActivityHistory(date=now.date())
        ActivityHistoryInterface._dump(new_ah)
        self.activity_history = new_ah
        return new_ah, minute_index

    def update(self, ah: types.ActivityHistory) -> None:
        """Update the activity history and dump it to the file system."""
        self.activity_history = ah
        if (time.time() - self.last_dump_time) >= (_MINUTES_BETWEEN_DUMPS * 60):
            ActivityHistoryInterface._dump(ah)

    def flush(self) -> None:
        """Dump the current activity history to the file system."""

        ah = self.activity_history
        if ah is not None:
            tum_esm_utils.files.dump_file(
                ActivityHistoryInterface._filepath(ah.date), ah.model_dump_json()
            )

    @staticmethod
    def _filepath(date: datetime.date) -> str:
        return os.path.join(
            _PROJECT_DIR, "logs", "activity", f"activity-{date.strftime('%Y-%m-%d')}.json"
        )

    @staticmethod
    def _dump(ah: types.ActivityHistory) -> None:
        tum_esm_utils.files.dump_file(
            ActivityHistoryInterface._filepath(ah.date), ah.model_dump_json()
        )
