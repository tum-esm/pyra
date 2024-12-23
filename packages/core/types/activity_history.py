from __future__ import annotations
import datetime
import os
import pydantic
import tum_esm_utils

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)


class ActivityHistory(pydantic.BaseModel):
    date: datetime.date
    core_is_running: list[int] = [0] * 24 * 60
    is_measuring: list[int] = [0] * 24 * 60
    has_errors: list[int] = [0] * 24 * 60
    camtracker_startups: list[int] = [0] * 24 * 60
    opus_startups: list[int] = [0] * 24 * 60
    cli_calls: list[int] = [0] * 24 * 60
    upload_is_running: list[int] = [0] * 24 * 60

    @staticmethod
    def filepath(date: datetime.date) -> str:
        return os.path.join(
            _PROJECT_DIR, "logs", "activity", f"activity-{date.strftime('%Y-%m-%d')}.json"
        )

    @staticmethod
    def get(date: datetime.date) -> ActivityHistory:
        path = ActivityHistory.filepath(date)
        if os.path.exists(path):
            return ActivityHistory.model_validate_json(tum_esm_utils.files.load_file(path))

        new_ah = ActivityHistory(date=date)
        new_ah.dump()
        return new_ah

    def dump(self) -> None:
        tum_esm_utils.files.dump_file(ActivityHistory.filepath(self.date), self.model_dump_json())

    @staticmethod
    def get_current_minute_index() -> int:
        now = datetime.datetime.now()
        return now.hour * 60 + now.minute
