import os
import filelock
import tum_esm_utils
from packages.core import main

_run_pyra_core_lock = filelock.FileLock(
    os.path.join(
        tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=2),
        "run_pyra_core.lock",
    ),
    timeout=0.5,
)

if __name__ == "__main__":
    try:
        _run_pyra_core_lock.acquire()
        try:
            main.run()
        finally:
            _run_pyra_core_lock.release()
    except filelock.Timeout:
        print("Aborting start: core process is already running")
