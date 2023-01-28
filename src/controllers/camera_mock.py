from controllers.camera_interface import CameraInterface
import numpy as np
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage



class CameraMock(CameraInterface):

    def initialize_camera(self):
        print("Camera Initialized")

    def get_next_frame(self):
        print("Captured image")
        #img = Image.open("C:\\Users\\cecel\\SeniorProject\\capturing\\src\\controllers\\cat.png")
        #return img
        return (0, )
        

    def capture_at_exposure(self, exposure):
        print("Captured image at exposure " + str(exposure))
        #img = Image.open("C:\\Users\\cecel\\SeniorProject\\capturing\\src\\controllers\\cat.png")
        #return img
        return (0, )

    def uninitialize_camera(self):
        print("Camera Uninitialized")

    def convert_nparray_to_QPixmap(self, img):
        return QPixmap(QImage("cat.png"))