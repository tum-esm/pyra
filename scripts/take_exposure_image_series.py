import time
import cv2 as cv
import numpy as np


class Helios:
    cam = None

    @staticmethod
    def init_cam(retries: int = 5):
        camera_id = 0

        Helios.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        Helios.cam.release()

        for _ in range(retries):
            Helios.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            if Helios.cam.isOpened():
                Helios.cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)  # width
                Helios.cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)  # height
                Helios.update_camera_settings(
                    exposure=-12, brightness=64, contrast=64, saturation=0, gain=0
                )
                print(f"using backend {Helios.cam.getBackendName()}")
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
            Helios.cam.set(cv.CAP_PROP_EXPOSURE, exposure)
            assert (
                Helios.cam.get(cv.CAP_PROP_EXPOSURE) == exposure
            ), f"could not set exposure to {exposure}"
        if brightness is not None:
            Helios.cam.set(cv.CAP_PROP_BRIGHTNESS, brightness)
            assert (
                Helios.cam.get(cv.CAP_PROP_BRIGHTNESS) == brightness
            ), f"could not set brightness to {brightness}"
        if contrast is not None:
            Helios.cam.set(cv.CAP_PROP_CONTRAST, contrast)
            assert (
                Helios.cam.get(cv.CAP_PROP_CONTRAST) == contrast
            ), f"could not set contrast to {contrast}"
        if saturation is not None:
            Helios.cam.set(cv.CAP_PROP_SATURATION, saturation)
            assert (
                Helios.cam.get(cv.CAP_PROP_SATURATION) == saturation
            ), f"could not set saturation to {saturation}"
        if gain is not None:
            Helios.cam.set(cv.CAP_PROP_GAIN, gain)
            assert Helios.cam.get(cv.CAP_PROP_GAIN) == gain, f"could not set gain to {gain}"

        # throw away some images after changing settings
        for i in range(2):
            Helios.cam.read()

    @staticmethod
    def take_image(retries: int = 5):
        assert Helios.cam is not None, "camera is not initialized yet"
        assert Helios.cam.isOpened(), "camera is not open"
        for _ in range(retries + 1):
            ret, frame = Helios.cam.read()
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
        for e in range(-12, 0):
            Helios.update_camera_settings(exposure=e)
            image = Helios.take_image()
            exposure_results.append({"exposure": e, "mean": np.mean(image)})
        print(exposure_results)
        return min(exposure_results, key=lambda r: abs(r["mean"] - 100))["exposure"]


if __name__ == "__main__":
    print(f"Initializing Helios camera")

    Helios.init_cam()
    print(f"successfully initialized camera")

    best_exposure = Helios.get_best_exposure()
    print(f"best_exposure = {best_exposure}")

    Helios.update_camera_settings(exposure=best_exposure)

    sample_image = Helios.take_image()
    print(np.mean(sample_image))
    cv.imwrite(f"sample-image-exposure-{best_exposure}.jpg", sample_image)

    Helios.cam.release()
    cv.destroyAllWindows()
