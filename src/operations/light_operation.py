from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

'''
Light Operation for Setting the Exposure of the Pixilink Camera
Written by Cecelia Ahrens
'''
class LightOp(Operation):
    main = None
    exposure1 = 1
    exposure2 = 0.66
    exposure3 = 1.5
    exposure4 = 2
    size = None

    '''Starts Light Operation'''
    def on_start(self):
        #start thread, move worker to thread
        self.main.thread = QThread()
        self.main.worker = ExposureWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.size = self.main.lightLevel0.size()

        self.main.thread.started.connect(self.main.worker.run)

        #disable select light level buttons until all snapshots have been taken
        self.main.lightLevel0.setEnabled(False)
        self.main.lightLevel1.setEnabled(False)
        self.main.lightLevel2.setEnabled(False)
        self.main.lightLevel3.setEnabled(False)

        #connect slots
        self.main.worker.img1.connect(self.tl_display)
        self.main.worker.img2.connect(self.tr_display)
        self.main.worker.img3.connect(self.bl_display)
        self.main.worker.img4.connect(self.br_display)
        self.main.worker.finished.connect(self.finished)

        self.main.thread.start()

    '''Cancel Light Operation'''
    def cancel(self):
        self.main.camera_control.reset_exposure()
        self.main.worker.Cancelled = False
        self.main.thread.quit()
        self.main.led_control.turn_off()

    '''Finish light operation and allow the user to select light level'''
    def finished(self):
        self.main.thread.quit()
        self.main.camera_control.reset_exposure()
        self.main.led_control.turn_off()
        self.main.lightLevel0.setEnabled(True)
        self.main.lightLevel1.setEnabled(True)
        self.main.lightLevel2.setEnabled(True)
        self.main.lightLevel3.setEnabled(True)

    '''Saves exposure level'''
    def save_level(self, exposure):
        self.main.camera_control.save_exposure(exposure)
        #print(self.main.camera_control.exposure)
        self.finished()

    '''Displays image top left button'''
    def tl_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel0.width() -24,self.main.lightLevel0.height() -24)
        self.main.lightLevel0.setIconSize(size)
        self.main.lightLevel0.setIcon(icon)

    '''Displays image in top right button'''
    def tr_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel1.width() -24,self.main.lightLevel1.height() -24)
        self.main.lightLevel1.setIconSize(size)
        self.main.lightLevel1.setIcon(icon)
    
    '''Displays image in bottom left button'''
    def bl_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel2.width() -24,self.main.lightLevel2.height() -24)
        self.main.lightLevel2.setIconSize(size)
        self.main.lightLevel2.setIcon(icon)

    '''Displays image in bottom right button'''
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

        # Take photo at x1 exposure
        frame1 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure1*self.main.camera_control.exposureArray[11])
        self.img1.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame1))
        #time.sleep(0.5) # 500 ms
        if self.cancelled:
            #print("manual cancel")
            self.main.camera_control.uninitialize_camera()
            return
        
        # Take photo at x0.66 exposure
        frame2 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure2*self.main.camera_control.exposureArray[11])
        self.img2.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame2))
        #time.sleep(0.5) # 500 ms
        if self.cancelled:
            #print("manual cancel")
            self.main.camera_control.uninitialize_camera()
            return
        
        # Take photo at x1.5 exposure
        frame3 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure3*self.main.camera_control.exposureArray[11])
        self.img3.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame3))
        #time.sleep(0.5) # 500 ms
        if self.cancelled:
            #print("manual cancel")
            self.main.camera_control.uninitialize_camera()
            return
        
        # Take photo at x2 exposure
        frame4 = self.main.camera_control.capture_at_exposure(self.main.light_op.exposure4*self.main.camera_control.exposureArray[11])
        self.img4.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame4))

        self.main.camera_control.uninitialize_camera()
        self.finished.emit()
