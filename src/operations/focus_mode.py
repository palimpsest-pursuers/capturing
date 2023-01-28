from operations.operation import Operation
import time

import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from matplotlib import pyplot as plt

#from operations.camera_capture import FocusWorker

class FocusMode(Operation):
    """
    """
    ui = None

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.ui.LargeDisplay.isVisible()

        #start thread, move worker to thread
        self.ui.thread = QThread()
        self.ui.worker = FocusWorker()
        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.worker.ui = self.ui

        #connect slots
        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.sharedFrame.connect(self.updateFrame)
        self.ui.worker.sharpness.connect(self.updateSharpness)

        self.ui.thread.start()
        

    def cancel(self):
        """"""
        self.ui.worker.notCancelled = False
        self.ui.infobox.setText('Operation Canceled')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
        self.ui.change_operation(self.ui.idle_op)

    def finished(self):
        self.ui.infobox.setText('Operation Finished')
        #self.ui.camera_control.uninitialize_camera()
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)

    '''def convert_nparray_to_QPixmap(self, img):
        frame = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        h, w = img.shape[:2]
        bytesPerLine = 3 * w
        qimage = QImage(frame.data, w, h, bytesPerLine, QImage.Format.Format_RGB888) 
        return QPixmap(qimage)'''

    def updateFrame(self, n):
        print(type(n))
        pixmap = n #self.convert_nparray_to_QPixmap(n)
        # self.label.setPixmap(pixmap)
        # self.label.resize(pixmap.width(),pixmap.height())
        self.ui.LargeDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))
        
        # self.resize(pixmap.width(),pixmap.height())

    def updateSharpness(self, n):
        self.ui.infobox.setText(f"Sharpness: {n}")

class FocusWorker(QObject):
    sharedFrame = pyqtSignal(QPixmap)
    sharpness = pyqtSignal(int)
    notCancelled = True
    ui = None

    def run(self):
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11]) #630 nm (red)
        # Initialize the camera
        self.ui.camera_control.initialize_camera()
        while self.notCancelled:
            frame = self.ui.camera_control.get_next_frame()
            img = self.ui.camera_control.convert_nparray_to_QPixmap(frame)
            self.sharedFrame.emit(img)

            time.sleep(0.5) # 500 ms
        self.ui.camera_control.uninitialize_camera()
        
        