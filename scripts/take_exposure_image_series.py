import time
import cv2 as cv


class VBDSD:
    cam = None

    @staticmethod
    def init_cam(retries: int = 5):
        """
        init_cam(int id): Connects to the camera with id and sets its parameters.
        If successfully connected, the function returns an instance object of the
        camera, otherwise None will be returned.
        """
        camera_id = 0

        VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
        VBDSD.cam.release()

        for _ in range(retries):
            VBDSD.cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
            time.sleep(1)
            if VBDSD.cam.isOpened():
                VBDSD.cam.set(3, 1280)  # width
                VBDSD.cam.set(4, 720)  # height
                VBDSD.update_camera_settings(
                    exposure=-12, brightness=64, contrast=64, saturation=0, gain=0
                )
                VBDSD.cam.read()  # throw away first picture
                VBDSD.change_exposure()

    @staticmethod
    def update_camera_settings(
        exposure: int = None,
        brightness: int = None,
        contrast: int = None,
        saturation: int = None,
        gain: int = None,
    ):
        if exposure is not None:
            VBDSD.cam.set(15, exposure)
        if brightness is not None:
            VBDSD.cam.set(10, brightness)
        if contrast is not None:
            VBDSD.cam.set(11, contrast)
        if saturation is not None:
            VBDSD.cam.set(12, saturation)
        if gain is not None:
            VBDSD.cam.set(14, gain)

    @staticmethod
    def take_image(exposure: int, retries: int = 5):
        VBDSD.update_camera_settings(exposure=exposure)
        for _ in range(retries + 1):
            ret, frame = VBDSD.cam.read()
            if ret:
                cv.imwrite(f"sample-exposure-{exposure}.jpg", frame)
                return True
        return False


def main():

    print(f"Initializing VBDSD camera")

    while True:
        VBDSD.init_cam()
        if VBDSD.cam is not None:
            print()
            time.sleep(10)
            print(f"could not init camera, sleeping 10 seconds")
            break

    print(f"successfully initialized camera")

    # retry with change_exposure(1) if status fail
    for exposure in range(-20, 1):
        was_successful = VBDSD.take_image(exposure)
        assert was_successful, f"could not take image for exposure {exposure}"

    print(f"all done!")
