from datetime import datetime
import os
import traceback
import filelock

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(dir(os.path.abspath(__file__))))))
INFO_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "info.log")
DEBUG_LOG_FILE = os.path.join(PROJECT_DIR, "logs", "debug.log")
LOG_FILES_LOCK = os.path.join(PROJECT_DIR, "logs", ".logs.lock")

# The logging module behaved very weird with the setup we have
# therefore I am just formatting and appending the log lines
# manually. Doesn't really make a performance difference


class Logger:
    last_iterations_log_lines: list[str] = []
    this_iterations_log_lines: list[str] = []

    def __init__(self, origin="pyra.core"):
        self.origin = origin

    def debug(self, message: str):
        self._write_log_line("DEBUG", message)

    def info(self, message: str):
        self._write_log_line("INFO", message)

    def warning(self, message: str):
        self._write_log_line("WARNING", message)

    def error(self, message: str):
        self._write_log_line("ERROR", message)

    def exception(self, e: Exception):
        # TODO: Attach traceback to message string
        tb = "\n".join(traceback.format_exception(e))
        self._write_log_line("EXCEPTION", f"{type(e).__name__} occured: {tb}")

    def _write_log_line(self, level: str, message: str):
        timestamp = datetime.utcnow()
        log_string = f"{timestamp} - {self.origin} - {level} - {message}\n"
        with filelock.FileLock(LOG_FILES_LOCK):
            with open(DEBUG_LOG_FILE, "a") as f1:
                f1.write(log_string)
            if level != "DEBUG":
                with open(INFO_LOG_FILE, "a") as f2:
                    f2.write(log_string)
