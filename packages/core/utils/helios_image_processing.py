import datetime
import os
from typing import Any, Optional
from PIL import Image, ImageDraw
import skimage
import numpy as np

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_LOGS_DIR = os.path.join(_PROJECT_DIR, "logs")
_IMG_DIR = os.path.join(_LOGS_DIR, "helios")


class HeliosImageProcessing:
    """Class for processing images from the Helios camera.

    See https://pyra.esm.ei.tum.de/docs/user-guide/tum-enclosure-and-helios#what-does-helios-do
    for more information on Helios."""

    def _get_lense_crop_contrast(
        image: np.ndarray,
        cx: float,
        cy: float,
        radius: float,
    ) -> float:
        """If you cut the image into two parts given a circle with center cx, cy and radius,
        this function returns the difference in mean color between the two parts."""

        rr, cc = skimage.draw.disk((cy, cx), radius, shape=image.shape)
        inner_mask = np.zeros(image.shape, dtype=np.uint8)
        inner_mask[rr, cc] = 1
        outer_mask = np.ones(image.shape, dtype=np.uint8) - inner_mask
        return abs(
            (np.sum(image * inner_mask) / np.sum(inner_mask))
            - (np.sum(image * outer_mask) / np.sum(outer_mask))
        )

    def get_lense_position(bw_image: np.ndarray) -> Optional[tuple[float, float, float]]:
        """Determine the position of the lense in the image."""

        bw_image = bw_image * (60 / np.mean(bw_image))

        # run canny edge detection
        edges = skimage.feature.canny(bw_image, sigma=7, low_threshold=3, high_threshold=10)

        # computing possible radii of lense
        image_height = min(bw_image.shape)
        min_lense_size = round(image_height * 0.5 * 0.85)
        max_lense_size = round(image_height * 0.5 * 1.15)
        lense_radii = np.arange(min_lense_size, max_lense_size, 2)

        # pick the 50 best circles
        hough_res = skimage.transform.hough_circle(edges, lense_radii)
        _, cx, cy, radii = skimage.transform.hough_circle_peaks(
            hough_res,
            lense_radii,
            min_xdistance=2,
            min_ydistance=2,
            total_num_peaks=50,
        )
        if len(radii) == 0:
            return None

        # order the circles based on contrast
        contrasts: list[tuple[float, int]] = sorted(
            zip(
                [
                    HeliosImageProcessing._get_lense_crop_contrast(bw_image, cx[i], cy[i], radii[i])
                    for i in range(len(radii))
                ],
                range(len(radii)),
            ),
            key=lambda x: x[0],
            reverse=True,
        )

        # determine the best circle based on contrast and hough circle peaks
        ranking = zip(range(len(contrasts)), [x[1] for x in contrasts])
        sorted_ranking = sorted(ranking, key=lambda x: x[0] + x[1])
        best_circle_index = sorted_ranking[0][1]

        return cx[best_circle_index] * 2, cy[best_circle_index] * 2, radii[best_circle_index] * 2

    @staticmethod
    def _annotate_processed_image(
        bw_frame: np.ndarray[Any, Any],
        edge_fraction: float,
        circle_cx: int,
        circle_cy: int,
        circle_r: int,
    ) -> Image.Image:
        """Put text for edge fraction and mark circles in image."""
        rgb_frame = skimage.color.gray2rgb(bw_frame)

        # draw outer circle
        rr, cc = skimage.draw.circle_perimeter(circle_cy, circle_cx, circle_r, shape=bw_frame.shape)
        outer_circle = np.zeros(bw_frame.shape, dtype=np.uint8)
        outer_circle[rr, cc] = 1
        outer_circle = skimage.morphology.dilation(outer_circle, skimage.morphology.disk(2))

        # draw inner circle
        rr, cc = skimage.draw.circle_perimeter(
            circle_cy, circle_cx, round(circle_r * 0.9), shape=bw_frame.shape
        )
        inner_circle = np.zeros(bw_frame.shape, dtype=np.uint8)
        inner_circle[rr, cc] = 1
        inner_circle = skimage.morphology.dilation(inner_circle, skimage.morphology.disk(2))

        # combine images
        rgb_frame[:, :, 0] = rgb_frame[:, :, 0] + outer_circle
        rgb_frame[:, :, 2] = rgb_frame[:, :, 2] + inner_circle
        rgb_frame[rgb_frame > 1] = 1

        # add text
        pil_image = Image.fromarray((rgb_frame * 255).astype(np.uint8))
        draw = ImageDraw.Draw(pil_image)
        draw.text((10, 10), f"{edge_fraction * 100:.2f}%", (255, 255, 255))
        draw.text((10, 30), f"{datetime.datetime.now()}", (255, 255, 255))

        return pil_image

    @staticmethod
    def _adjust_image_brightness_in_post(
        frame: np.ndarray[Any, Any],
        target_image_brightness: float,
    ) -> np.ndarray[Any, Any]:
        mean_brightness = np.mean(frame)
        scaling_factor = target_image_brightness / mean_brightness
        return frame * scaling_factor  # type: ignore

    @staticmethod
    def get_edge_fraction(
        rgb_frame: np.ndarray[Any, Any],
        station_id: str,
        edge_color_threshold: int,
        target_pixel_brightness: float,
        lense_circle: tuple[int, int, int],
        save_images_to_archive: bool = False,
        save_current_image: bool = False,
    ) -> float:
        """For a given frame determine the number of "edge pixels" with
        respect to the inner 90% of the lense diameter and the "status".
        The status is 1 when the edge pixels are above the given threshold
        and 0 otherwise."""

        # convert the image to black and white
        bw_frame: np.ndarray = skimage.color.rgb2gray(rgb_frame)

        # adjust the brightness of the frame to a target value
        evenly_lit_frame: np.ndarray = bw_frame * (target_pixel_brightness / np.mean(bw_frame))

        # transform image from 1280x720 to 640x360
        # downscaled_image: np.ndarray = skimage.transform.rescale(evenly_lit_frame, 0.5)

        # only consider edges and make them bold
        edges_dilated: np.ndarray = skimage.morphology.dilation(
            skimage.feature.canny(
                evenly_lit_frame,
                sigma=7,
                low_threshold=round(edge_color_threshold * 0.8),
                high_threshold=edge_color_threshold,
            ),
            skimage.morphology.disk(2),
        ).astype(np.uint8)

        # blacken the outer 10% of the circle radius
        inner_mask = np.zeros(evenly_lit_frame.shape, dtype=np.uint8)
        cc, rr = skimage.draw.disk(
            center=(lense_circle[1], lense_circle[0]),
            radius=lense_circle[2] * 0.9,
            shape=evenly_lit_frame.shape,
        )
        inner_mask[cc, rr] = 1
        edges_dilated = edges_dilated * inner_mask

        # determine how many pixels inside the circle are made up of "edge pixels"
        pixels_inside_circle: int = np.sum(3.141592 * pow(lense_circle[2] * 0.9, 2))
        edge_fraction: float = 0
        if pixels_inside_circle != 0:
            edge_fraction = round(
                (np.sum(edges_dilated))  # type: ignore
                / pixels_inside_circle,
                6,
            )

        if save_images_to_archive or save_current_image:
            now = datetime.datetime.now()
            img_timestamp = now.strftime("%Y%m%d-%H%M%S")
            img_directory_path = os.path.join(_IMG_DIR, now.strftime("%Y%m%d"))
            if not os.path.exists(img_directory_path):
                os.mkdir(img_directory_path)

            edge_fraction_str = str(edge_fraction) + ("0" * (8 - len(str(edge_fraction))))
            processed_frame = HeliosImageProcessing._annotate_processed_image(
                edges_dilated, edge_fraction, *lense_circle
            )

            if save_images_to_archive or save_current_image:
                raw_image = Image.fromarray(
                    (skimage.color.gray2rgb(bw_frame) * 255).astype(np.uint8)
                )
                if save_images_to_archive:
                    raw_image.save(
                        os.path.join(
                            img_directory_path,
                            f"{station_id}-{img_timestamp}-{edge_fraction_str}-raw.jpg",
                        ),
                    )
                    processed_frame.save(
                        os.path.join(
                            img_directory_path,
                            f"{station_id}-{img_timestamp}-{edge_fraction_str}-edges.jpg",
                        ),
                    )
                if save_current_image:
                    raw_image.save(
                        os.path.join(_LOGS_DIR, "current-helios-view-raw.jpg"),
                    )
                    processed_frame.save(
                        os.path.join(_LOGS_DIR, "current-helios-view-processed.jpg"),
                    )

        return edge_fraction
