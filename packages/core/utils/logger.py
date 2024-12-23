import datetime
import os
import traceback
from typing import Optional
import time

import filelock

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_DEBUG_LOG_FILE = os.path.join(_PROJECT_DIR, "logs", "debug.log")
_LOG_FILES_LOCK = os.path.join(_PROJECT_DIR, "logs", ".logs.lock")


def _get_log_line_datetime(log_line: str) -> Optional[datetime.datetime]:
    """Returns the date, if a log line is starting with a valid date."""
    try:
        assert len(log_line) >= 35
        return datetime.datetime.strptime(log_line[:35], "%Y-%m-%d %H:%M:%S.%f UTC%z")
    except (AssertionError, ValueError):
        return None


class Logger:
    """A reimplementation of the logging module.

    _Why?_ The `logging` module from the Python standard library is kind
    of hard to configure with some setups we have on the server-side. That
    is why we have decided to use a custom logging class in some of our
    bigger projects instead.

    This class is simply formatting log lines, appending them to the
    log files and providing a simple API.
    """

    last_archive_time = datetime.datetime.now().astimezone()

    def __init__(
        self,
        origin: str = "pyra.core",
        just_print: bool = False,
    ) -> None:
        """Create a new logger instance.

        With `just_print = True`, the log lines will be formatted
        like in the log files but only printed to the console."""

        self.origin: str = origin
        self.just_print: bool = just_print

    def debug(self, message: str) -> None:
        """Write a debug log (to debug only). Used for verbose output"""
        self._write_log_line("DEBUG", message)

    def info(self, message: str) -> None:
        """Write an info log (to debug and info)"""
        self._write_log_line("INFO", message)

    def warning(self, message: str) -> None:
        """Write a warning log (to debug and info)"""
        self._write_log_line("WARNING", message)

    def error(self, message: str) -> None:
        """Write an error log (to debug and info)"""
        self._write_log_line("ERROR", message)

    def exception(self, e: Exception) -> None:
        """Log the traceback of an exception"""
        tb = "\n".join(traceback.format_exception(e))
        self._write_log_line("EXCEPTION", f"{type(e).__name__} occured: {tb}")

    def _write_log_line(self, level: str, message: str) -> None:
        """Format the log line string and write it to "logs/debug.log"
        and possibly "logs/info.log"""
        now = datetime.datetime.now().astimezone()
        log_string = (
            f"{now.strftime('%Y-%m-%d %H:%M:%S.%f UTC%z')} - {self.origin} - {level} - {message}\n"
        )
        if self.just_print:
            print(log_string, end="")
        else:
            with filelock.FileLock(_LOG_FILES_LOCK, timeout=10):
                # current logs that only contains from the last 5-10 minutes
                with open(_DEBUG_LOG_FILE, "a") as f1:
                    f1.write(log_string)

                # archive that contains all log lines
                with open(
                    os.path.join(
                        _PROJECT_DIR, "logs", "archive", f"{now.strftime('%Y-%m-%d')}-debug.log"
                    ),
                    "a",
                ) as f:
                    f.write(log_string)

        # Archive lines older than 5 minutes, every 5 minutes
        if (now - Logger.last_archive_time).total_seconds() > 300:
            Logger.archive()
            Logger.last_archive_time = now

    @staticmethod
    def archive() -> None:
        """Only keep the lines from the last 5 minutes in "logs/debug.log"."""

        with filelock.FileLock(_LOG_FILES_LOCK, timeout=10):
            with open(_DEBUG_LOG_FILE, "r") as f:
                log_lines_in_file = f.readlines()
            if len(log_lines_in_file) == 0:
                return

            lines_to_be_kept: list[str] = []
            latest_log_time_to_keep = datetime.datetime.now().astimezone() - datetime.timedelta(
                minutes=5
            )
            for index, line in enumerate(log_lines_in_file):
                line_time = _get_log_line_datetime(line)
                print(line_time, latest_log_time_to_keep)
                if line_time is not None:
                    if line_time > latest_log_time_to_keep:
                        lines_to_be_kept = log_lines_in_file[index:]
                        break

            with open(_DEBUG_LOG_FILE, "w") as f:
                f.writelines(lines_to_be_kept)
