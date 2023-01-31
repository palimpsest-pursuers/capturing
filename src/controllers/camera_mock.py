from controllers.camera_interface import CameraInterface
from PyQt5.QtGui import QPixmap, QImage



class CameraMock(CameraInterface):

    
    def __init__(self):
        self.ORIGINAL_EXPOSURE = 1

    def initialize_camera(self):
        print("Camera Initialized")

    def capture(self):
        print("Captured image")
        #img = Image.open("C:\\Users\\cecel\\SeniorProject\\capturing\\src\\controllers\\cat.png")
        #return img
        return (0, )

    def capture_at_exposure(self, exposure):
        print("Captured image at exposure " + str(exposure))
        #img = Image.open("C:\\Users\\cecel\\SeniorProject\\capturing\\src\\controllers\\cat.png")
        #return img
        return (0, )

    def save_exposure(self, exposure):
        self.exposure = exposure
        print("Saving exposure at " + str(exposure))

    def reset_exposure(self):
        self.exposure = self.ORIGINAL_EXPOSURE

    def uninitialize_camera(self):
        print("Camera Uninitialized")

    def convert_nparray_to_QPixmap(self, img):
        return QPixmap(QImage("C:\\Users\\cecel\\SeniorProject\\capturing\\src\\controllers\\cat.png"))