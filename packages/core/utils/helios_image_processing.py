import datetime
import os
from typing import Any, Optional
from PIL import Image, ImageDraw
import skimage
import numpy as np

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_LOGS_DIR = os.path.join(_PROJECT_DIR, "logs")


class HeliosImageProcessing:
    """Class for processing images from the Helios camera.

    See https://pyra.esm.ei.tum.de/docs/user-guide/tum-enclosure-and-helios#what-does-helios-do
    for more information on Helios."""

    @staticmethod
    def _get_lense_crop_contrast(
        image: np.ndarray[Any, Any],
        cx: float,
        cy: float,
        radius: float,
    ) -> float:
        """If you cut the image into two parts given a circle with center cx, cy and radius,
        this function returns the difference in mean color between the two parts."""

        rr, cc = skimage.draw.disk((cy, cx), radius, shape=image.shape)
        inner_mask: np.ndarray[Any, Any] = np.zeros(image.shape, dtype=np.uint8)
        inner_mask[rr, cc] = 1
        outer_mask: np.ndarray[Any, Any] = np.ones(image.shape, dtype=np.uint8) - inner_mask
        return float(
            abs(
                (np.sum(image * inner_mask) / np.sum(inner_mask))
                - (np.sum(image * outer_mask) / np.sum(outer_mask))
            )
        )

    @staticmethod
    def get_lense_position(
        frame: np.ndarray[Any, Any],
        use_downscaling: bool = False,
    ) -> Optional[tuple[int, int, int]]:
        """Determine the position of the lense in the image."""

        bw_frame = skimage.color.rgb2gray(frame)
        if use_downscaling:
            bw_frame = skimage.transform.rescale(bw_frame, 0.5)

        # adjust frame color
        bw_frame = bw_frame * (60 / np.mean(bw_frame))

        # run canny edge detection
        edges = skimage.feature.canny(bw_frame, sigma=7, low_threshold=3, high_threshold=10)

        # computing possible radii of lense
        image_height = min(bw_frame.shape)
        min_lense_size = round(image_height * 0.5 * 0.45)
        max_lense_size = round(image_height * 0.5 * 1.2)
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
                    HeliosImageProcessing._get_lense_crop_contrast(bw_frame, cx[i], cy[i], radii[i])
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

        multiplier = 2 if use_downscaling else 1
        return (
            round(cx[best_circle_index] * multiplier),
            round(cy[best_circle_index] * multiplier),
            round(radii[best_circle_index] * multiplier),
        )

    @staticmethod
    def annotate_processed_image(
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
        draw.text((10, 10), f"{datetime.datetime.now()}", (255, 255, 255), font_size=35)
        draw.text((10, 50), f"{edge_fraction * 100:.2f}%", (255, 255, 255), font_size=35)

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
        image_name: Optional[str] = None,
        image_directory: str = os.path.join(_LOGS_DIR, "helios", "%Y%m%d"),
    ) -> float:
        """For a given frame determine the number of "edge pixels" with
        respect to the inner 90% of the lense diameter and the "status".
        The status is 1 when the edge pixels are above the given threshold
        and 0 otherwise."""

        # convert the image to black and white
        bw_frame: np.ndarray[Any, Any] = skimage.color.rgb2gray(rgb_frame)

        # adjust the brightness of the frame to a target value
        evenly_lit_frame: np.ndarray[Any, Any] = bw_frame * (
            target_pixel_brightness / np.mean(bw_frame)
        )
        evenly_lit_frame[evenly_lit_frame > 255] = 255

        # transform image from 1280x720 to 640x360
        # downscaled_image: np.ndarray = skimage.transform.rescale(evenly_lit_frame, 0.5)

        # only consider edges and make them bold
        edges_dilated: np.ndarray[Any, Any] = skimage.morphology.dilation(
            skimage.feature.canny(
                evenly_lit_frame,
                sigma=7,
                low_threshold=round(edge_color_threshold * (1 / 7) * 0.5),
                high_threshold=round(edge_color_threshold * (1 / 7)),
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

        # optionally save images to local disk
        if save_images_to_archive or save_current_image:
            now = datetime.datetime.now()
            img_timestamp = now.strftime("%Y%m%d-%H%M%S")

            edge_fraction_str = str(edge_fraction) + ("0" * (8 - len(str(edge_fraction))))
            raw_image = Image.fromarray((skimage.color.gray2rgb(evenly_lit_frame)).astype(np.uint8))
            processed_image = HeliosImageProcessing.annotate_processed_image(
                edges_dilated, edge_fraction, *lense_circle
            )

            # used in post-analysis
            if save_images_to_archive:
                img_directory_path = os.path.join(
                    os.path.dirname(image_directory),
                    now.strftime(os.path.basename(image_directory)),
                )
                os.makedirs(img_directory_path, exist_ok=True)
                image_slug = os.path.join(
                    img_directory_path, f"{station_id}-{img_timestamp}-{edge_fraction_str}"
                )
                if image_name is not None:
                    image_slug = os.path.join(img_directory_path, image_name)
                raw_image.save(image_slug + "-raw.jpg")
                processed_image.save(image_slug + "-processed.jpg")

            # used by the UI
            if save_current_image:
                raw_image.save(
                    os.path.join(_LOGS_DIR, "current-helios-view-raw.jpg"),
                )
                processed_image.save(
                    os.path.join(_LOGS_DIR, "current-helios-view-processed.jpg"),
                )

        return float(edge_fraction)
