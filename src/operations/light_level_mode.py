from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from operations.camera_capture import ExposureWorker

class LightLevelMode(Operation):
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
        self.ui.LargeDisplay.clear()
        self.ui.LargeDisplay.setVisible(False)

        self.ui.LightDisplayTL.clear()
        self.ui.LightDisplayTR.clear()
        self.ui.LightDisplayBL.clear()
        self.ui.LightDisplayBR.clear()

        self.ui.LightDisplayTL.setVisible(True)
        self.ui.LightDisplayTR.setVisible(True)
        self.ui.LightDisplayBL.setVisible(True)
        self.ui.LightDisplayBR.setVisible(True)
        print("Light level mode on")

        #start thread, move worker to thread
        self.ui.thread = QThread()
        self.ui.worker = ExposureWorker()
        self.ui.worker.moveToThread(self.ui.thread)

        #connect slots
        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.frame1.connect(self.tl_display)
        self.ui.worker.frame2.connect(self.tr_display)
        self.ui.worker.frame3.connect(self.bl_display)
        self.ui.worker.frame4.connect(self.br_display)

        self.ui.thread.start()

    def cancel(self):
        """"""
        self.ui.worker.Cancelled = False
        self.ui.infobox.setText('Operation Canceled')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
        self.ui.LightDisplayTL.setVisible(False)
        self.ui.LightDisplayTR.setVisible(False)
        self.ui.LightDisplayBL.setVisible(False)
        self.ui.LightDisplayBR.setVisible(False)
        self.ui.change_operation(self.ui.idle_op)

    def finished(self):
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
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