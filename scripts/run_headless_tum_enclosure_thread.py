"""Runs the TUM enclosure thread standalone, does not generate logs, but only prints."""

import sys
import threading
import tum_esm_utils

sys.path.append(tum_esm_utils.files.rel_to_abs_path(".."))

from packages.core import threads

if __name__ == "__main__":
    threads.AEMETEnclosureThread.main(logs_lock=threading.Lock(), headless=True)
