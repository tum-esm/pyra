from datetime import datetime
import math
import os
from typing import Optional
import cv2 as cv
import numpy as np

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))
IMG_DIR = os.path.join(PROJECT_DIR, "logs", "helios")


class HeliosImageProcessing:

    # circle code adapted from https://stackoverflow.com/a/39074620/8255842
    @staticmethod
    def _get_circle_mask(
        img_shape: tuple[int, int],
        radius: int,
        center_x: int,
        center_y: int,
    ) -> cv.Mat:
        """
        input: image width/height, circle radius/center_x/center_y

        output: binary mask (2D array) like
        [[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
        [0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0]
        [0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0]
        [0 0 0 0 1 1 1 1 1 1 1 1 1 0 0 0]
        [0 0 0 0 1 1 1 1 1 1 1 1 1 0 0 0]
        [0 0 0 0 1 1 1 1 1 1 1 1 1 0 0 0]
        [0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0]
        [0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0]
        [0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0]]
        """

        y, x = np.indices(img_shape)
        return (np.abs(np.hypot(center_x - x, center_y - y)) < radius).astype(np.uint8)

    @staticmethod
    def _moving_average(
        xs: list[float],
        n: int = 3,
    ) -> list[float]:
        ret = np.cumsum(xs)
        ret[n:] = ret[n:] - ret[:-n]
        return list(ret[n - 1 :] / n)

    @staticmethod
    def _get_binary_mask(frame: cv.Mat) -> cv.Mat:
        """
        input: gray image matrix (2D matrix) with integer values for each pixel
        output: binary mask (same shape) that has 0s for dark pixels and 1s for bright pixels
        """

        blurred_image = cv.medianBlur(frame, 7)
        # kmeans only supports matrices with datatype np.float32 !!
        # apply kmeans (bin colors to the 2 most dominant ones)
        _, kmeans_labels, kmeans_centers = cv.kmeans(
            data=np.array(blurred_image.flatten(), dtype=np.float32),
            K=2,
            bestLabels=None,
            criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0),
            attempts=5,
            flags=cv.KMEANS_PP_CENTERS,
        )

        # labels array is [1, 0, 0, 1,...] = one label (= color index) for each pixel
        binary_mask = np.reshape(kmeans_labels, frame.shape)

        # flip colors if color with index 0 is the bright one
        if kmeans_centers[0][0] > kmeans_centers[1][0]:
            binary_mask = (binary_mask - 1) * -1

        return binary_mask

    @staticmethod
    def _get_circle_location(grayscale_image: cv.Mat) -> Optional[tuple[int, int, int]]:
        """
        input: binary mask (2D array) like
        [[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
        [0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0]
        [0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0]
        [0 0 0 0 1 1 1 1 1 1 1 1 1 0 0 0]
        [0 0 0 0 1 1 1 1 1 1 1 1 1 0 0 0]
        [0 0 0 0 1 1 1 1 1 1 1 1 1 0 0 0]
        [0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0]
        [0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0]
        [0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0]]

        output: center_x, center_y, r
        """
        image_height, image_width = grayscale_image.shape[0], grayscale_image.shape[1]

        circles = cv.HoughCircles(
            grayscale_image,
            cv.HOUGH_GRADIENT,
            dp=20,
            minDist=250,
            minRadius=round((image_height * 0.85) * 0.5),
            maxRadius=round((image_height * 1.15) * 0.5),
        )

        if circles is None:
            return None

        # get the circle that is closest to the image center
        x, y, r = min(
            np.round(circles[0, :]).astype("int"),
            key=lambda c: math.pow(c[0] - (image_width * 0.5), 2)  # type: ignore
            + pow(c[1] - (image_height * 0.5), 2),
        )
        return round(x), round(y), round(r)

    @staticmethod
    def add_markings_to_image(
        img: cv.Mat, edge_fraction: float, circle_cx: int, circle_cy: int, circle_r: int
    ) -> cv.Mat:
        """Put text for edge fraction and mark circles in image"""
        img = cv.circle(img, (circle_cx, circle_cy), circle_r, (100, 0, 0), 2)
        img = cv.circle(img, (circle_cx, circle_cy), round(circle_r * 0.9), (100, 0, 0), 2)
        img = HeliosImageProcessing.add_text_to_image(img, f"{round(edge_fraction * 100, 2)}%")
        return img

    @staticmethod
    def add_text_to_image(
        img: cv.Mat, text: str, color: tuple[int, int, int] = (200, 0, 0)
    ) -> cv.Mat:
        """Put some text on the bottom left of an image"""
        cv.putText(
            img,
            text=text,
            org=(10, img.shape[0] - 15),
            fontFace=None,
            fontScale=0.8,
            color=color,
            thickness=2,
        )
        return img

    @staticmethod
    def get_edge_fraction(frame: cv.Mat, save_image: bool = False) -> float:
        """
        For a given frame determine the number of "edge pixels" with
        respect to the inner 90% of the lense diameter and the "status".
        The status is 1 when the edge pixels are above the given threshold
        and 0 otherwise.

        1. Downscale image (faster processing)
        2. Convert to grayscale image
        3. Determine position and size of circular opening
        4. Determine edges in image (canny edge filter)
        5. Only consider edges inside 0.9 * circleradius

        Returns the "edge pixel fraction"
        """

        # transform image from 1280x720 to 640x360
        downscaled_image = cv.resize(frame, None, fx=0.5, fy=0.5)

        # for each rgb pixel [234,234,234] only consider the gray value (234)
        grayscale_image = cv.cvtColor(downscaled_image, cv.COLOR_BGR2GRAY)

        # determine lense position and size from binary mask
        circle_location = HeliosImageProcessing._get_circle_location(grayscale_image)
        if circle_location is None:
            return 0
        else:
            circle_cx, circle_cy, circle_r = circle_location

        # only consider edges and make them bold
        edges_only: cv.Mat = np.array(cv.Canny(grayscale_image, 40, 40), dtype=np.float32)
        edges_only_dilated: cv.Mat = cv.dilate(
            edges_only, cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
        )

        # blacken the outer 10% of the circle radius
        edges_only_dilated *= HeliosImageProcessing._get_circle_mask(
            edges_only_dilated.shape, round(circle_r * 0.9), circle_cx, circle_cy
        )

        # determine how many pixels inside the circle are made up of "edge pixels"
        pixels_inside_circle: int = np.sum(3.141592 * pow(circle_r * 0.9, 2))
        edge_fraction: float = 0
        if pixels_inside_circle != 0:
            edge_fraction = round((np.sum(edges_only_dilated) / 255) / pixels_inside_circle, 6)

        if save_image:
            now = datetime.now()
            img_timestamp = now.strftime("%Y%m%d-%H%M%S")
            img_directory_path = os.path.join(IMG_DIR, now.strftime("%Y%m%d"))
            if not os.path.exists(img_directory_path):
                os.mkdir(img_directory_path)

            edge_fraction_str = str(edge_fraction) + ("0" * (8 - len(str(edge_fraction))))
            raw_img_name = f"{img_timestamp}-{edge_fraction_str}-raw.jpg"

            processed_img_name = f"{img_timestamp}-{edge_fraction_str}-processed.jpg"
            processed_frame = HeliosImageProcessing.add_markings_to_image(
                edges_only_dilated, edge_fraction, circle_cx, circle_cy, circle_r
            )

            cv.imwrite(os.path.join(img_directory_path, raw_img_name), frame)
            cv.imwrite(os.path.join(img_directory_path, processed_img_name), processed_frame)

        return edge_fraction