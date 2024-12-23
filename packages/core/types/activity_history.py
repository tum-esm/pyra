from __future__ import annotations
import datetime
import pydantic


class NewActivityHistory(pydantic.baseModel):
    date: datetime.date
    core_is_running: list[int] = [0] * 24 * 20
    is_measuring: list[int] = [0] * 24 * 20
    has_errors: list[int] = [0] * 24 * 20
    camtracker_startups: list[int] = [0] * 24 * 20
    opus_startups: list[int] = [0] * 24 * 20
    cli_calls: list[int] = [0] * 24 * 20
    upload_is_running: list[int] = [0] * 24 * 20
