import sys
import tum_esm_utils

sys.path.append(tum_esm_utils.files.rel_to_abs_path(".."))

from packages.core import threads

if __name__ == "__main__":
    threads.HeliosThread.main(headless=True)
