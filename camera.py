from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time


class Camera:

    def __init__(self, resolution=(1920, 1080)):
        self.piCam = PiCamera()
        self.h_fov = 39.5   # 62.2
        self.v_fov = None   # 48.8
        if resolution is not None:
            self.piCam.resolution = resolution  # SetUp camera resolution
        self.h_size = self.piCam.resolution[0]
        self.v_size = self.piCam.resolution[1]

    def take_and_save_photo(self, path):
        raw_capture = PiRGBArray(self.piCam)
        time.sleep(0.5)
        self.piCam.capture(raw_capture, format="bgr", use_video_port=True)
        image = raw_capture.array
        #image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imwrite(path, image)
