import sys
import time
from PIL import Image
import numpy as np
import skimage
import tqdm
import tum_esm_utils
import cv2 as cv

sys.path.append(tum_esm_utils.files.rel_to_abs_path("../.."))

from packages.core import threads
from packages.core import utils


def camera_id_exists(camera_id: int) -> bool:
    """Check if a camera with the given ID exists."""
    if sys.platform.startswith("win"):
        camera = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
    else:
        camera = cv.VideoCapture(camera_id)
    time.sleep(0.1)  # Allow time for the camera to initialize
    exists = camera.isOpened()
    camera.release()
    return exists


def find_available_camera_ids() -> list[int]:
    """Find an available camera IDs."""
    available_ids = []
    for i in tqdm.tqdm(range(10)):  # Check camera IDs from 0 to 9
        if camera_id_exists(i):
            available_ids.append(i)
            print(f"Camera ID {i} is available.")
    return available_ids


if __name__ == "__main__":
    logger = utils.Logger("helios-finding", lock=None, just_print=True)

    available_camera_ids = find_available_camera_ids()
    print(f"Available camera IDs: {available_camera_ids}")

    for camera_id in available_camera_ids:
        logger.info(f"Testing camera with ID: {camera_id}")
        try:
            helios_interface = threads.helios_thread.HeliosInterface(
                logger=logger,
                camera_id=camera_id,
                initialization_tries=3,
            )
        except Exception as e:
            logger.error(f"Failed to initialize HeliosInterface for camera ID {camera_id}: {e}")
            continue

        for i in range(5):
            img = helios_interface.take_image()
            # make image grayscale
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            img_object = Image.fromarray((img.astype(np.uint8)))
            path = tum_esm_utils.files.rel_to_abs_path(
                f"./finding/find-helios-camera-id-{camera_id}-take-{i + 1}.jpg"
            )
            img_object.save(path)
            logger.info(f"Saved image {i} to {path}")
