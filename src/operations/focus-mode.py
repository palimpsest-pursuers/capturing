from pixelinkWrapper import*
from ctypes import*
import time
import numpy as np
import sys, signal

import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from matplotlib import pyplot as plt


#interrupt handler
def interrupt_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


# Just to define our image buffer;  One that's large enough for the Pixelink camera being used
MAX_WIDTH = 5000   # in pixels
MAX_HEIGHT = 5000  # in pixels
MAX_BYTES_PER_PIXEL = 3

"""
A robust wrapper around PxLApi.getNextFrame.
This will handle the occasional error that can be returned by the API because of timeouts. 
Note that this should only be called when grabbing images from a camera NOT currently configured for triggering. 
"""
def get_next_frame(hCamera, frame, maxNumberOfTries):

    ret = (PxLApi.ReturnCode.ApiUnknownError,)

    for i in range(maxNumberOfTries):
        ret = PxLApi.getNextNumPyFrame(hCamera, frame)
        if PxLApi.apiSuccess(ret[0]):
            return ret
        else:
            # If the streaming is turned off, or worse yet -- is gone?
            # If so, no sense in continuing.
            if PxLApi.ReturnCode.ApiStreamStopped == ret[0] or \
                PxLApi.ReturnCode.ApiNoCameraAvailableError == ret[0]:
                return ret
            else:
                print("getNextFrame returned %i" % ret[0])

    # Ran out of tries, so return whatever the last error was.
    return ret


def main():

  
    
    return 0


class Worker(QObject):
    sharedFrame = pyqtSignal(np.ndarray)
    sharpness = pyqtSignal(int)

    def run(self):
        # Initialize the camera
        ret = PxLApi.initialize(0)
        if not(PxLApi.apiSuccess(ret[0])):
            print("Error: Unable to initialize a camera! rc = %i" % ret[0])
            return 1

        hCamera = ret[1]

        # get proper camera size, create frame from that
        ret = PxLApi.getFeature(hCamera, PxLApi.FeatureId.ROI)
        params = ret[2]
        roiWidth = params[PxLApi.RoiParams.WIDTH]
        roiHeight = params[PxLApi.RoiParams.HEIGHT]

        frame = np.zeros([int(roiHeight),int(roiWidth)], dtype=np.uint8)

        # Start the stream
        ret = PxLApi.setStreamState(hCamera, PxLApi.StreamState.START)

        # If stream started successfully
        if PxLApi.apiSuccess(ret[0]):
            while True:
                ret = get_next_frame(hCamera, frame, 5)

                #frame was successful
                if PxLApi.apiSuccess(ret[0]):
                    #update frame
                    self.sharedFrame.emit(frame)

                    #calculate sharpness
                    gy, gx = np.gradient(frame)
                    gnorm = np.sqrt(gx**2 + gy**2)
                    sharpness = 1/(np.average(gnorm))
                    self.sharpness.emit(sharpness)

                #frame was unsuccessful
                else:
                    print("Too many errors encountered, exiting")
                    sys.exit(-1)

                    
                time.sleep(0.5) # 500 ms
                
        else:
            print("setStreamState with StreamState.START failed, rc = %i" % ret[0])

        #turn off stream state 
        PxLApi.setStreamState(hCamera, PxLApi.StreamState.STOP)
        assert PxLApi.apiSuccess(ret[0]), "setStreamState with StreamState.STOP failed"

        PxLApi.uninitialize(hCamera)
        assert PxLApi.apiSuccess(ret[0]), "uninitialize failed"

def convert_nparray_to_QPixmap(img):
    frame = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    h, w = img.shape[:2]
    bytesPerLine = 3 * w
    qimage = QImage(frame.data, w, h, bytesPerLine, QImage.Format.Format_RGB888) 
    return QPixmap(qimage)


class App(QWidget):

    def updateFrame(self, n):
        pixmap = convert_nparray_to_QPixmap(n)
        # self.label.setPixmap(pixmap)
        # self.label.resize(pixmap.width(),pixmap.height())
        self.label.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))
        
        # self.resize(pixmap.width(),pixmap.height())

    def updateSharpness(self, n):
        self.sharpnessBox.setText(f"Sharpness: {n}")

    def runFocusMode(self):
        #start thread, move worker to thread
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        #connect slots
        self.thread.started.connect(self.worker.run)
        self.worker.sharedFrame.connect(self.updateFrame)
        self.worker.sharpness.connect(self.updateSharpness)

        self.thread.start()


    def __init__(self):
        super().__init__()
        self.title = 'MISHA - Focus Mode Demo'
        self.left = 480
        self.top = 270
        self.width = 810
        self.height = 572
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Create widget
        self.label = QLabel(self)
        self.label.resize(960,540)

        self.sharpnessBox = QLabel(self)
        self.sharpnessBox.resize(960,100)
        self.sharpnessBox.setFont(QFont('Helvetica', 20))
        self.sharpnessBox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.sharpnessBox.move(10,540)
        self.runFocusMode()
        
        self.show()

if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())