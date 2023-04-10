from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

import numpy as np

class FlatsOp(Operation):
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

    def finished(self):
        self.main.thread.quit()
        self.main.led_control.turn_off()
        self.main.setPage(self.main.flatsSteps, self.main.flatsStep2)

    def updateFrame(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.flatsStep1View.width(), self.main.flatsStep1View.height(), QtCore.Qt.KeepAspectRatio))
        self.main.flatsStep1View.setScene(scene)

    def updateZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.flatsStep1Zoom.width(), self.main.flatsStep1Zoom.height(), QtCore.Qt.KeepAspectRatio))
        self.main.flatsStep1Zoom.setScene(scene)

    def updateHistogram(self, hist):
        pass

    def updateWavelength(self, wavelength):
        self.main.flatsStep1Wave.setText("Wavelength: " + wavelength)

    def updateProgressBar(self, value):
        self.main.flatsProgressBar.setValue(value)


class CaptureWorker(QObject):
    sharedFrame = pyqtSignal(QPixmap)
    zoomedFrame = pyqtSignal(QPixmap)
    wavelength = pyqtSignal(str)
    histogram = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int)
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
            self.sharedFrame.emit(img)
            self.main.led_control.turn_off()
            #histogram = np.histogram(frame)
            #self.histogram.emit(frame)
            
            zoom = self.main.camera_control.zoom(frame,float(4.0))
            zImg = self.main.camera_control.convert_nparray_to_QPixmap(zoom)
            self.zoomedFrame.emit(zImg)
            self.main.cube_builder.add_flat_image(frame)
            time.sleep(0.5) # 500 ms
            self.progress.emit((1/len(self.main.led_control.wavelength_list))*100*i)
            i += 1
        self.main.camera_control.uninitialize_camera()
        self.main.led_control.turn_off()
        self.main.flats_op.finished()
