from controllers.camera_interface import CameraInterface
from PyQt5.QtGui import QPixmap, QImage
import cv2

class BlackflyController(CameraInterface):
    def initialize_camera(self):
        self.capture_ = cv2.VideoCapture(0)
        print("Camera Initialized")

    def capture(self):
        ret, frame = self.capture_.read()
        return frame

    def capture_at_exposure(self, exposure):
        #TODO: is exposure even real?
        ret, frame = self.capture_.read()
        return frame

    def convert_nparray_to_QPixmap(self, img):
        # frame = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        frame = img
        h, w = img.shape[:2]
        bytesPerLine = 3 * w
        qimage = QImage(frame.data, w, h, bytesPerLine, QImage.Format.Format_RGB888) 
        return QPixmap(qimage)

    def uninitialize_camera(self):
        self.capture_.release()

    
        