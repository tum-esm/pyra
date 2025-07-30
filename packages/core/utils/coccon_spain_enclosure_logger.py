import datetime
import os

import tum_esm_utils

from packages.core import types

_PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)


class COCCONSpainEnclosureLogger:
    """A class to save the current COCCON Spain Enclosure state to a log file."""

    @staticmethod
    def log(config: types.Config, state: types.StateObject) -> None:
        now = datetime.datetime.now()
        timestamp = now.timestamp()
        datetime_string = now.isoformat()

        log_line = [
            timestamp,
            datetime_string,
            state.position.sun_elevation,
            # TODO: add the variables you want
        ]
        stringed_log_line = [str(item).lower() if item is not None else "null" for item in log_line]
        current_log_file = os.path.join(
            _PROJECT_DIR,
            "logs",
            "coccon-spain-enclosure",
            f"{config.general.station_id}-coccon-spain-enclosure-logs-{now.strftime('%Y-%m-%d')}.csv",
        )
        if not os.path.isfile(current_log_file):
            with open(current_log_file, "w") as f:
                f.write("timestamp,datetime,sun_elevation\n")
        with open(current_log_file, "a") as f:
            f.write(",".join(stringed_log_line) + "\n")
