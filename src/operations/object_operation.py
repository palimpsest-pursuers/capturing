from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import numpy as np

class ObjectOp(Operation):
    main = None

    def on_start(self):
        self.main.thread = QThread()
        self.main.worker = CaptureWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main

        self.main.thread.started.connect(self.main.worker.run)
        self.main.worker.sharedFrame.connect(self.updateFrame)
        self.main.worker.zoomedFrame.connect(self.updateZoomed)
        self.main.worker.wavelength.connect(self.updateWavelength)
        self.main.worker.histogram.connect(self.updateHistogram)
        self.main.worker.progress.connect(self.updateProgressBar)

        self.main.thread.start()

    def cancel(self):
        """"""
        self.main.worker.cancelled = True
        self.main.thread.quit()
        self.main.led_control.turn_off()

    def updateFrame(self, n):
        print(type(n))
        pixmap = n 
        self.ui.LargeDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))
        #self.ui.middleRightDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))

    def updateZoomed(self, n):
        print(type(n))
        pixmap = n 
        self.ui.middleRightDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))

    def updateWavelength(self, wavelength):
        self.ui.infobox.setText("Wavelength: " + wavelength)

    def updateProgressBar(self, int):
        pass
class CaptureWorker(QObject):
    sharedFrame = pyqtSignal(QPixmap)
    zoomedFrame = pyqtSignal(QPixmap)
    wavelength = pyqtSignal(str)
    histogram = pyqtSignal(np.ndarray)
    cancelled = False
    main = None

    def run(self):
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[11]) #630 nm (red)
        self.main.camera_control.initialize_camera()
        i = 0
        for wavelength in self.main.led_control.wavelength_list:
            
            if self.cancelled:
                break
            self.wavelength.emit(wavelength)
            self.main.led_control.turn_on(wavelength)

            frame = self.main.camera_control.capture()

            
            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
            #self.sharedFrame.emit(img)
            #self.ui.led_control.turn_off()
            #histogram = np.histogram(frame)
            #self.histogram.emit(frame)
            
            zoom = self.main.camera_control.zoom(frame,float(4.0))
            zImg = self.main.camera_control.convert_nparray_to_QPixmap(zoom)
            self.zoomedFrame.emit(zImg)
            self.main.cube_builder.add_raw_image(frame, wavelength)
            #time.sleep(0.5) # 500 ms
            i += 1
        self.main.camera_control.uninitialize_camera()
        self.main.led_control.turn_off()
