from abc import ABC, abstractmethod
import cv2
from PyQt5.QtGui import QPixmap, QImage

class CameraInterface(ABC):
    exposure = None

    @abstractmethod
    def initialize_camera(self) -> None:
        pass

    @abstractmethod
    def get_next_frame(self) -> tuple:
        pass

    @abstractmethod
    def capture_at_exposure(self, exposure) -> tuple:
        pass

    @abstractmethod
    def uninitialize_camera(self) -> None:
        pass

    def convert_nparray_to_QPixmap(self, img):
        frame = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        h, w = img.shape[:2]
        bytesPerLine = 3 * w
        qimage = QImage(frame.data, w, h, bytesPerLine, QImage.Format.Format_RGB888) 
        return QPixmap(qimage)

    def set_exposure(self, exposure):
        self.exposure = exposure

    def get_exposure(self):
        return self.exposure