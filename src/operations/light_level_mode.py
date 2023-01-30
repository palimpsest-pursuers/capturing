from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

#from operations.camera_capture import ExposureWorker

class LightLevelMode(Operation):
    """

    """
    ui = None
    exposure1 = 1
    exposure2 = 0.66
    exposure3 = 1.5
    exposure4 = 2

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.ui.LargeDisplay.clear()
        self.ui.LargeDisplay.setVisible(False)
        self.ui.TopRightLabel.setVisible(False)

        self.ui.LightDisplayTL.setVisible(True)
        self.ui.LightDisplayTR.setVisible(True)
        self.ui.LightDisplayBL.setVisible(True)
        self.ui.LightDisplayBR.setVisible(True)
        print("Light level mode on")

        #start thread, move worker to thread
        self.ui.thread = QThread()
        self.ui.worker = ExposureWorker()
        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.worker.ui = self.ui

        #connect slots
        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.frame1.connect(self.tl_display)
        self.ui.worker.frame2.connect(self.tr_display)
        self.ui.worker.frame3.connect(self.bl_display)
        self.ui.worker.frame4.connect(self.br_display)

        self.ui.thread.start()

    def cancel(self):
        """"""
        self.save_level(self.exposure1)
        self.ui.worker.Cancelled = False
        self.ui.infobox.setText('Operation Canceled')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
        self.ui.LightDisplayTL.setVisible(False)
        self.ui.LightDisplayTR.setVisible(False)
        self.ui.LightDisplayBL.setVisible(False)
        self.ui.LightDisplayBR.setVisible(False)
        self.ui.change_operation(self.ui.idle_op)

    def finished_pics(self):
        self.ui.infobox.setText('Select Light Level')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
        self.ui.LightDisplayTL.setEnabled(True)
        self.ui.LightDisplayTR.setEnabled(True)
        self.ui.LightDisplayBL.setEnabled(True)
        self.ui.LightDisplayBR.setEnabled(True)

    def finished(self):
        self.ui.infobox.setText('Operation Finished\nExposure Set to ' + str(self.ui.camera_control.get_exposure()))
        self.ui.LightDisplayTL.setVisible(False)
        self.ui.LightDisplayTR.setVisible(False)
        self.ui.LightDisplayBL.setVisible(False)
        self.ui.LightDisplayBR.setVisible(False)
        self.ui.change_operation(self.ui.idle_op)
    
    def tl_display(self, img):
        self.ui.LightDisplayTL.setPixmap(img)
        

    def tr_display(self, img):
        self.ui.LightDisplayTR.setPixmap(img)
        
    
    def bl_display(self, img):
        self.ui.LightDisplayBL.setPixmap(img)
        


    def br_display(self, img):
        self.ui.LightDisplayBR.setPixmap(img)
        

    def save_level(self, exposure):
        self.ui.camera_control.set_exposure(exposure)
        self.ui.LightDisplayTL.setEnabled(False)
        self.ui.LightDisplayTR.setEnabled(False)
        self.ui.LightDisplayBL.setEnabled(False)
        self.ui.LightDisplayBR.setEnabled(False)
        self.finished()

class ExposureWorker(QObject):
    frame1 = pyqtSignal(QPixmap)
    frame2 = pyqtSignal(QPixmap)
    frame3 = pyqtSignal(QPixmap)
    frame4 = pyqtSignal(QPixmap)
    cancelled = False
    ui = None

    def run(self):
        img = self.ui.camera_control.capture_at_exposure(self.ui.level_op.exposure1)
        self.frame1 = self.ui.camera_control.convert_nparray_to_QPixmap(img)
        time.sleep(0.5) # 500 ms
        if self.cancelled:
            return
        img2 = self.ui.camera_control.capture_at_exposure(self.ui.level_op.exposure2)
        self.frame2 = self.ui.camera_control.convert_nparray_to_QPixmap(img2)
        time.sleep(0.5) # 500 ms
        if self.cancelled:
            return
        img3 = self.ui.camera_control.capture_at_exposure(self.ui.level_op.exposure3)
        self.frame3 = self.ui.camera_control.convert_nparray_to_QPixmap(img3)
        time.sleep(0.5) # 500 ms
        if self.cancelled:
            return
        img4 = self.ui.camera_control.capture_at_exposure(self.ui.level_op.exposure4)
        self.frame4 = self.ui.camera_control.convert_nparray_to_QPixmap(img4)
        self.ui.level_op.finished_pics()