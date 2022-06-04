from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time


class Camera:

    def __init__(self, resolution=(1920, 1080)):
        """
        Initializes the piCam, sets up the desired resolution, and stores the required attributes of the class.

        @param resolution: Resolution for the camera.
        """

        self.piCam = PiCamera()
        self.h_fov = 39.5   # The supposed horizontal aperture of the cam is 62.2, but we measured it ourselves and we got ~39.5
        self.v_fov = None   # 48.8
        if resolution is not None:
            self.piCam.resolution = resolution  # SetUp camera resolution
        self.h_size = self.piCam.resolution[0]
        self.v_size = self.piCam.resolution[1]

    def take_and_save_photo(self, path):
        """
        Takes a photo and saves it to the specified path.

        @param path: Path indicating where to save the photo.
        """
        raw_capture = PiRGBArray(self.piCam)
        time.sleep(0.5)
        self.piCam.capture(raw_capture, format="bgr", use_video_port=True)
        image = raw_capture.array
        cv2.imwrite(path, image)
