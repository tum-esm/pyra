from datetime import datetime, timedelta
import json
import os
import traceback
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
INFO_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "info.log")
DEBUG_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "debug.log")
LOG_FILES_LOCK = os.path.join(PROJECT_DIR, "logs", ".logs.lock")

# The logging module behaved very weird with the setup we have
# therefore I am just formatting and appending the log lines
# manually. Doesn't really make a performance difference


def log_line_has_time(log_line: str) -> bool:
    """Returns true when a give log line (string) starts
    with a valid date. This is not true for exception
    tracebacks. This log line time is used to determine
    which file to archive logs lines into."""
    try:
        assert len(log_line) >= 10
        datetime.strptime(log_line[:10], "%Y-%m-%d")
        return True
    except:
        return False


class Logger:
    last_archive_time = datetime.now()

    def __init__(self, origin: str = "pyra.core", just_print: bool = False) -> None:
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
        now = datetime.now()
        utc_offset = round((datetime.now() - datetime.utcnow()).total_seconds() / 3600, 1)
        if round(utc_offset) == utc_offset:
            utc_offset = round(utc_offset)

        log_string = (
            f"{now} UTC{'' if utc_offset < 0 else '+'}{utc_offset} "
            + f"- {self.origin} - {level} - {message}\n"
        )
        if self.just_print:
            print(log_string, end="")
        else:
            with filelock.FileLock(LOG_FILES_LOCK):
                with open(DEBUG_LOG_FILE, "a") as f1:
                    f1.write(log_string)
                if level != "DEBUG":
                    with open(INFO_LOG_FILE, "a") as f2:
                        f2.write(log_string)

        # Archive lines older than 60 minutes, every 10 minutes
        if (now - Logger.last_archive_time).total_seconds() > 600:
            Logger.archive(keep_last_hour=True)
            Logger.last_archive_time = now

    @staticmethod
    def archive(keep_last_hour: bool = False) -> None:
        """
        Move all log lines in "logs/info.log" and "logs/debug.log" into
        an archive file ("logs/archive/YYYYMMDD-debug.log", "...info.log").

        With keep_last_hour = True, log lines less than an hour old will
        remain.
        """
        with filelock.FileLock(LOG_FILES_LOCK):
            with open(DEBUG_LOG_FILE, "r") as f:
                log_lines_in_file = f.readlines()
            if len(log_lines_in_file) == 0:
                return

            lines_to_be_archived = []
            lines_to_be_kept = []
            latest_time = str(datetime.now() - timedelta(hours=(1 if keep_last_hour else 0)))
            line_time = log_lines_in_file[0][:26]
            for index, line in enumerate(log_lines_in_file):
                if log_line_has_time(line):
                    line_time = line[:26]
                if line_time > latest_time:
                    lines_to_be_archived = log_lines_in_file[:index]
                    lines_to_be_kept = log_lines_in_file[index:]
                    break

            with open(DEBUG_LOG_FILE, "w") as f:
                f.writelines(lines_to_be_kept)
            with open(INFO_LOG_FILE, "w") as f:
                f.writelines([l for l in lines_to_be_kept if " - DEBUG - " not in l])

            if len(lines_to_be_archived) == 0:
                return

            archive_log_date_groups: dict[str, dict[str, list[str]]] = {}
            line_date = lines_to_be_archived[0][:10].replace("-", "")
            for line in lines_to_be_archived:
                if log_line_has_time(line):
                    line_date = line[:10].replace("-", "")
                if line_date not in archive_log_date_groups.keys():
                    archive_log_date_groups[line_date] = {"debug": [], "info": []}
                archive_log_date_groups[line_date]["debug"].append(line)
                if " - DEBUG - " not in line:
                    archive_log_date_groups[line_date]["info"].append(line)

            for date in archive_log_date_groups.keys():
                for t in ["info", "debug"]:
                    filename = os.path.join(PROJECT_DIR, "logs", "archive", f"{date}-{t}.log")
                    with open(filename, "a") as f:
                        f.writelines(archive_log_date_groups[date][t] + [""])

    @staticmethod
    def log_activity_event(event_label: str) -> None:
        """
        Log things like:
        * start-measurements
        * stop-measurements
        * error-occured
        * errors-resolved
        * start-core
        * stop-core
        """
        assert event_label in [
            "start-measurements",
            "stop-measurements",
            "error-occured",
            "errors-resolved",
            "start-core",
            "stop-core",
        ]
        now = datetime.now()
        filename = now.strftime("activity-%Y-%m-%d.json")
        filepath = os.path.join(PROJECT_DIR, "logs", "activity", filename)

        with filelock.FileLock(LOG_FILES_LOCK):
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    current_activity = json.load(f)
            else:
                current_activity = []

            current_activity.append(
                {"localTime": now.strftime("%H:%M:%S"), "event": event_label}
            )

            with open(filepath, "w") as f:
                json.dump(current_activity, f, indent=4)
