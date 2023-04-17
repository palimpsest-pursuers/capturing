from abc import ABC, abstractmethod
import cv2
from PyQt5.QtGui import QPixmap, QImage
from scipy import ndimage
import numpy as np

class CameraInterface(ABC):
    ORIGINAL_EXPOSURE = None
    exposure = None
    sharpness = None

    exposureArray = [0.0045,0.0025,0.002,0.0028,
                    0.001,0.001,0.001,0.0024,
                    0.002,0.018,0.004,0.0035,
                    0.0025,0.011,0.01,0.05]


    @abstractmethod
    def initialize_camera(self) -> None:
        pass

    @abstractmethod
    def capture(self) -> tuple:
        pass

    @abstractmethod
    def capture_at_exposure(self, exposure) -> tuple:
        pass

    @abstractmethod
    def uninitialize_camera(self) -> None:
        pass

    @abstractmethod
    def reset_exposure(self):
        pass
    
    @abstractmethod
    def save_exposure(self, exposure):
        pass

    def zoom(self, img, zoom):
        h, w = img.shape[:2]

        zoom_tuple = (zoom,) * 2 + (1,) * (img.ndim - 2)

        zh = int(np.round(h / zoom))
        zw = int(np.round(w / zoom))
        top = (h - zh) // 2
        left = (w - zw) // 2

        out = ndimage.zoom(img[top:top+zh, left:left+zw], zoom_tuple)

        trim_top = ((out.shape[0] - h) // 2)
        trim_left = ((out.shape[1] - w) // 2)
        out = out[trim_top:trim_top+h, trim_left:trim_left+w]

        return out

    def convert_nparray_to_QPixmap(self, img):
        frame = cv2.cvtColor(img, cv2.)
        h, w = img.shape[:2]
        bytesPerLine = 3 * w
        qimage = QImage(img.data, w, h, bytesPerLine, QImage.Format.Format_Grayscale8) 
        return QPixmap(qimage)

    def get_exposure(self):
        return self.exposure

    def get_sharpness(self):
        return self.sharpness