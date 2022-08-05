import stat
import time
import cv2 as cv
import numpy as np


class VBDSD:
    cam = None

    @staticmethod
    def init_cam(retries: int = 5):
        camera_id = 0

        VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        VBDSD.cam.release()

        for _ in range(retries):
            VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            if VBDSD.cam.isOpened():
                VBDSD.cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)  # width
                VBDSD.cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)  # height
                VBDSD.update_camera_settings(
                    exposure=-12, brightness=64, contrast=64, saturation=0, gain=0
                )
                VBDSD.cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
                VBDSD.cam.read()  # throw away first picture
                print(f"using backend {VBDSD.cam.getBackendName()}")
                return
            else:
                time.sleep(2)

        raise Exception("could not initialize camera")

    @staticmethod
    def update_camera_settings(
        exposure: int = None,
        brightness: int = None,
        contrast: int = None,
        saturation: int = None,
        gain: int = None,
    ):
        if exposure is not None:
            VBDSD.cam.set(cv.CAP_PROP_EXPOSURE, exposure)
            assert (
                VBDSD.cam.get(cv.CAP_PROP_EXPOSURE) == exposure
            ), f"could not set exposure to {exposure}"
        if brightness is not None:
            VBDSD.cam.set(cv.CAP_PROP_BRIGHTNESS, brightness)
            assert (
                VBDSD.cam.get(cv.CAP_PROP_BRIGHTNESS) == brightness
            ), f"could not set brightness to {brightness}"
        if contrast is not None:
            VBDSD.cam.set(cv.CAP_PROP_CONTRAST, contrast)
            assert (
                VBDSD.cam.get(cv.CAP_PROP_CONTRAST) == contrast
            ), f"could not set contrast to {contrast}"
        if saturation is not None:
            VBDSD.cam.set(cv.CAP_PROP_SATURATION, saturation)
            assert (
                VBDSD.cam.get(cv.CAP_PROP_SATURATION) == saturation
            ), f"could not set saturation to {saturation}"
        if gain is not None:
            VBDSD.cam.set(cv.CAP_PROP_GAIN, gain)
            assert VBDSD.cam.get(cv.CAP_PROP_GAIN) == gain, f"could not set gain to {gain}"

    @staticmethod
    def take_image(retries: int = 5):
        assert VBDSD.cam is not None, "camera is not initialized yet"
        for _ in range(retries + 1):
            ret, frame = VBDSD.cam.read()
            if ret:
                return frame
        raise Exception("could not take image")

    @staticmethod
    def get_best_exposure() -> int:
        """
        determine the exposure, where the overall
        mean pixel value color is closest to 100
        """
        exposure_results = []
        for e in range(-13, 0):
            VBDSD.update_camera_settings(exposure=e)
            image = VBDSD.take_image()
            exposure_results.append({"exposure": e, "mean": np.mean(image)})
        return min(exposure_results, key=lambda r: abs(r["mean"] - 100))["exposure"]


if __name__ == "__main__":
    print(f"Initializing VBDSD camera")

    VBDSD.init_cam()
    print(f"successfully initialized camera")

    best_exposure = VBDSD.get_best_exposure()
    print(f"best_exposure = {best_exposure}")
    VBDSD.update_camera_settings(exposure=best_exposure)

    sample_image = VBDSD.take_image()
    cv.imwrite(f"sample-image-exposure-{abs(best_exposure)}.jpg")
