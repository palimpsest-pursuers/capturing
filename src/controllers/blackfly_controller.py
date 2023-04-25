import time
from controllers.camera_interface import CameraInterface
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
import cv2

class BlackflyController(CameraInterface):
    '''
    '''
    def initialize_camera(self):
        self.capture_ = cv2.VideoCapture(0)
        print("Camera Initialized")

    '''
    '''
    def capture(self):
        ret, frame = self.capture_.read()
        time.sleep(0.5) # 500 ms
        img_HLS = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        L = img_HLS
        u = np.mean(L)
        LP = cv2.Laplacian(L, cv2.CV_64F).var()
        self.sharpness = 1/np.sum(LP/u)*1000

        return img_HLS

    '''
    '''
    def capture_at_exposure(self, exposure):
        return self.capture()

    '''
    '''
    def uninitialize_camera(self):
        self.capture_.release()

    '''
    '''
    def reset_exposure(self):
        pass

    '''
    '''
    def save_exposure(self, exposure):
        pass


    
        