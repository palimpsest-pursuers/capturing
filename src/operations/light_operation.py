from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

class LightOp(Operation):
    main = None
    exposure1 = 1
    exposure2 = 0.66
    exposure3 = 1.5
    exposure4 = 2
    size = None


    def on_start(self):
        #start thread, move worker to thread
        self.main.thread = QThread()
        self.main.worker = ExposureWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.size = self.main.lightLevel0.size()

        #connect slots
        self.main.thread.started.connect(self.main.worker.run)
        #self.main.thread.disconnect.connect(self.main.light_op.cancel)
        self.main.worker.img1.connect(self.tl_display)
        self.main.worker.img2.connect(self.tr_display)
        self.main.worker.img3.connect(self.bl_display)
        self.main.worker.img4.connect(self.br_display)
        self.main.worker.finished.connect(self.finished)

        self.main.thread.start()

    def cancel(self):
        self.main.camera_control.reset_exposure()
        self.main.worker.Cancelled = False
        self.main.thread.quit()
        self.main.led_control.turn_off()

    def finished(self):
        self.main.thread.quit()
        self.main.camera_control.reset_exposure()
        self.main.led_control.turn_off()
        self.main.lightLevel0.setEnabled(True)
        self.main.lightLevel1.setEnabled(True)
        self.main.lightLevel2.setEnabled(True)
        self.main.lightLevel3.setEnabled(True)

    def save_level(self, exposure):
        self.main.camera_control.save_exposure(exposure)
        self.finished()

    def tl_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel0.width() -24,self.main.lightLevel0.height() -24)
        self.main.lightLevel0.setIconSize(size)
        self.main.lightLevel0.setIcon(icon)

    def tr_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel1.width() -24,self.main.lightLevel1.height() -24)
        self.main.lightLevel1.setIconSize(size)
        self.main.lightLevel1.setIcon(icon)
    
    def bl_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel2.width() -24,self.main.lightLevel2.height() -24)
        self.main.lightLevel2.setIconSize(size)
        self.main.lightLevel2.setIcon(icon)

    def br_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel3.width() -24,self.main.lightLevel3.height() -24)
        self.main.lightLevel3.setIconSize(size)
        self.main.lightLevel3.setIcon(icon)


class ExposureWorker(QObject):
    img1 = pyqtSignal(QPixmap)
    img2 = pyqtSignal(QPixmap)
    img3 = pyqtSignal(QPixmap)
    img4 = pyqtSignal(QPixmap)
    finished = pyqtSignal()
    cancelled = False
    main = None

    def run(self):
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[11]) #630 nm (red)
        # Initialize the camera
        self.main.camera_control.initialize_camera()

        frame1 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure1)
        self.img1.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame1))
        time.sleep(0.5) # 500 ms
        if self.cancelled:
            #print("manual cancel")
            self.main.camera_control.uninitialize_camera()
            return
        frame2 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure2)
        self.img2.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame2))
        #time.sleep(0.5) # 500 ms
        if self.cancelled:
            #print("manual cancel")
            self.main.camera_control.uninitialize_camera()
            return
        frame3 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure3)
        self.img3.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame3))
        #time.sleep(0.5) # 500 ms
        if self.cancelled:
            #print("manual cancel")
            self.main.camera_control.uninitialize_camera()
            return
        frame4 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure4)
        self.img4.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame4))

        self.main.camera_control.uninitialize_camera()
        self.finished.emit()
