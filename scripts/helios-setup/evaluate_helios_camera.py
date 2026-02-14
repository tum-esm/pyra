import sys
import time
import tum_esm_utils

sys.path.append(tum_esm_utils.files.rel_to_abs_path("../.."))

from packages.core import threads, utils, types

# ENTER CAMERA IT HERE
CAMERA_ID = 0

if __name__ == "__main__":
    logger = utils.Logger("helios-evaluation", lock=None, just_print=True)

    logger.info(f"Testing camera with ID: {CAMERA_ID}")
    helios_interface = threads.helios_thread.HeliosInterface(
        logger=logger,
        helios_config=types.config.HeliosConfig(
            camera_id=CAMERA_ID,
            evaluation_size=5,
            seconds_per_interval=10,
            min_seconds_between_state_changes=180,
            edge_pixel_threshold=40,
            edge_color_threshold=40,
            target_pixel_brightness=60,
            camera_brightness=50,
            camera_contrast=50,
            save_current_image=False,
            save_images_to_archive=False,
        ),
        initialization_tries=3,
    )
    lense_finder = threads.helios_thread.LenseFinder(logger)

    for i in range(5):
        rgb_frame = helios_interface.take_image()

        lense_finder.update_lense_position(rgb_frame)
        lense = lense_finder.current_lense
        if lense is None:
            logger.warning("No lense found in image -> not evaluating edge fraction")
            continue
        logger.info(f"Current lense position (x,y,r): {lense}")

        edge_fraction = utils.HeliosImageProcessing.get_edge_fraction(
            rgb_frame=rgb_frame,
            station_id="test",
            edge_color_threshold=40,
            target_pixel_brightness=60,
            lense_circle=lense,
            save_images_to_archive=True,
            image_directory=tum_esm_utils.files.rel_to_abs_path("./evaluation"),
            image_name=f"test-take-{i + 1}",
        )
        logger.debug(f"edge_fraction = {edge_fraction}")

        time.sleep(2)
