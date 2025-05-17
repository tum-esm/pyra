from typing import Optional
import datetime
import os
import traceback
import time
import threading

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_DEBUG_LOG_FILE = os.path.join(_PROJECT_DIR, "logs", "debug.log")


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
        origin: str,
        lock: threading.Lock,
        just_print: bool = False,
        main_thread: bool = False,
    ) -> None:
        """Create a new logger instance.

        With `just_print = True`, the log lines will be formatted
        like in the log files but only printed to the console."""

        self.origin = origin
        self.just_print = just_print
        self.main_thread = main_thread
        self.lock = lock
        self.pending_log_lines: list[str] = []
        self.last_successful_logging_time: float = time.time()

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

        def _log_to_file(l: str) -> None:
            l = "".join(self.pending_log_lines) + l
            # current logs that only contains from the last 5-10 minutes
            with open(_DEBUG_LOG_FILE, "a") as f1:
                f1.write(l)

            # archive that contains all log lines
            with open(
                os.path.join(
                    _PROJECT_DIR, "logs", "archive", f"{now.strftime('%Y-%m-%d')}-debug.log"
                ),
                "a",
            ) as f:
                f.write(l)

            self.last_successful_logging_time = time.time()
            self.pending_log_lines = []

        if self.just_print:
            print(log_string, end="")
        else:
            try:
                with self.lock:
                    _log_to_file(log_string)
            except TimeoutError:
                self.pending_log_lines.append(log_string)
                if (time.time() - self.last_successful_logging_time) > 300:
                    raise TimeoutError("Could not acquire logs lock for 5 minutes.")

        # Archive lines older than 5 minutes, every 5 minutes
        if self.main_thread:
            if (now - Logger.last_archive_time).total_seconds() > 300:
                Logger.archive(self.lock)
                Logger.last_archive_time = now

    @staticmethod
    def archive(lock: threading.Lock) -> None:
        """Only keep the lines from the last 5 minutes in "logs/debug.log"."""

        for i in range(5):
            try:
                with lock:
                    with open(_DEBUG_LOG_FILE, "r") as f:
                        log_lines_in_file = f.readlines()
                    if len(log_lines_in_file) == 0:
                        return

                    lines_to_be_kept: list[str] = []
                    latest_log_time_to_keep = (
                        datetime.datetime.now().astimezone() - datetime.timedelta(minutes=5)
                    )
                    for index, line in enumerate(log_lines_in_file):
                        line_time = _get_log_line_datetime(line)
                        if line_time is not None:
                            if line_time > latest_log_time_to_keep:
                                lines_to_be_kept = log_lines_in_file[index:]
                                break

                    with open(_DEBUG_LOG_FILE, "w") as f:
                        f.writelines(lines_to_be_kept)
            except TimeoutError:
                if i == 4:
                    raise TimeoutError("Could not acquire logs lock to archive the current logs.")
                time.sleep(1)
