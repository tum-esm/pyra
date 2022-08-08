import cv2 as cv
import numpy as np


class ImageProcessing:

    # circle code adapted from https://stackoverflow.com/a/39074620/8255842
    @staticmethod
    def get_circle_mask(img_shape: tuple[int, int], radius: int, center_x: int, center_y: int):
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
    def moving_average(xs, n=3):
        ret = np.cumsum(xs)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1 :] / n

    @staticmethod
    def get_binary_mask(frame):
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
    def get_circle_location(binary_mask):
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

        output: center_x, center_y, r (all floats)
        """

        # number of bright pixels in each image row
        row_sums = np.sum(binary_mask, axis=1)

        # WxH mask: 0 in black pixels, column-index in bright pixels

        row_indices, col_indices = np.indices(binary_mask.shape)
        row_indices *= binary_mask
        col_indices *= binary_mask

        radius = np.max(ImageProcessing.moving_average(row_sums, n=3)) / 2
        center_y = np.mean(row_indices, where=(row_indices != 0))
        center_x = np.mean(col_indices, where=(col_indices != 0))

        return round(center_x), round(center_y), round(radius)

    @staticmethod
    def add_markings_to_image(
        img, edge_fraction: int, circle_cx: int, circle_cy: int, circle_r
    ):
        img = cv.circle(img, (circle_cx, circle_cy), circle_r, (100, 0, 0), 2)
        img = cv.circle(img, (circle_cx, circle_cy), round(circle_r * 0.9), (100, 0, 0), 2)
        img = ImageProcessing.add_text_to_image(img, f"{round(edge_fraction * 100, 2)}%")
        return img

    @staticmethod
    def add_text_to_image(img, text):
        cv.putText(
            img,
            text=text,
            org=(10, img.shape[0] - 15),
            fontFace=None,
            fontScale=0.8,
            color=(200, 0, 0),
            thickness=2,
        )
        return img
