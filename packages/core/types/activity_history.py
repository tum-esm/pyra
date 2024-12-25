import datetime
import pydantic


class ActivityHistory(pydantic.BaseModel):
    date: datetime.date
    core_is_running: list[int] = [0] * 24 * 60
    is_measuring: list[int] = [0] * 24 * 60
    has_errors: list[int] = [0] * 24 * 60
    camtracker_startups: list[int] = [0] * 24 * 60
    opus_startups: list[int] = [0] * 24 * 60
    cli_calls: list[int] = [0] * 24 * 60
    upload_is_running: list[int] = [0] * 24 * 60
