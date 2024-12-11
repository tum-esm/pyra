import datetime
import glob
import os
import time
from typing import Literal


def read_last_file_line(
    file_path: str,
    ignore_trailing_whitespace: bool = True,
) -> str:
    """Reads the last non empty line of a file"""

    with open(file_path, "rb") as f:
        f.seek(-1, os.SEEK_END)

        if ignore_trailing_whitespace:
            while f.read(1) in [b"\n", b" "]:
                try:
                    f.seek(-2, os.SEEK_CUR)
                except OSError:
                    # reached the beginning of the file
                    return ""

            f.seek(-1, os.SEEK_CUR)
            # now the cursor is right before the last
            # character that is not a newline or a space

        last_line: bytes = b""
        new_character: bytes = b""
        while True:
            new_character = f.read(1)
            if new_character == b"\n":
                break
            last_line += new_character
            f.seek(-2, os.SEEK_CUR)

        return last_line.decode().strip()[::-1]


def find_most_recent_files(
    directory_path: str,
    time_limit: float,
    time_indicator: Literal["created", "modified"],
) -> list[str]:
    """Find the most recently modified files in a directory.

    Args:
        directory_path: The path to the directory to search.
        time_limit: The time limit in seconds.

    Returns:
        A list of the most recently modified files sorted by modification time
        (the most recent first) and only including files modified within the
        time limit.
    """
    if time_limit <= 0:
        return []

    current_timestamp = time.time()
    files = [f for f in glob.glob(os.path.join(directory_path, "*")) if os.path.isfile(f)]
    modification_times = [os.path.getmtime(f) for f in files]
    creation_times = [os.path.getctime(f) for f in files]
    times = modification_times if time_indicator == "modified" else creation_times
    merged = sorted(
        [(f, t) for f, t in list(zip(files, times)) if t >= (current_timestamp - time_limit)],
        key=lambda x: x[1],
        reverse=True,
    )
    return [f for f, t in merged]


def parse_verbal_timedelta_string(timedelta_string: str) -> datetime.timedelta:
    """Parse a timedelta string like "1 year, 2 days, 3 hours, 4 mn" into a timedelta object.

    The string does not have to contain all components. The only requirement is that the
    components are separated by ", "."""

    years = days = hours = minutes = 0

    # Parse each part
    for part in timedelta_string.split(", "):
        if "year" in part:
            years = int(part.split(" ")[0])
        elif "day" in part:
            days = int(part.split(" ")[0])
        elif "hour" in part:
            hours = int(part.split(" ")[0])
        elif ("mn" in part) or ("min" in part):
            minutes = int(part.split(" ")[0])

    # Convert years to days (approximate, assuming 365 days per year)
    days += years * 365

    # Create and return the timedelta object
    return datetime.timedelta(days=days, hours=hours, minutes=minutes)
