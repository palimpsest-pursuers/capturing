from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import debugpy

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
        self.main.worker.finished.connect(self.finished)

        self.main.flatsProgressBar.setRange(0,16)
        self.main.flatsProgressBar.setValue(0)

        self.main.cube_builder.flats_array = []
        self.main.cube_builder.revert_final()
        self.main.thread.start()

    def cancel(self):
        """"""
        self.main.worker.cancelled = True
        self.main.thread.quit()
        self.main.led_control.turn_off()
        self.main.cube_builder.revert_final()
        self.main.cube_builder.flats_array = []

    def finished(self):
        self.main.thread.quit()
        self.main.led_control.turn_off()
        self.main.setPage(self.main.flatsSteps, self.main.flatsStep2)
        self.main.flatsDisplay(0)

    def updateFrame(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.flatsStep1View.width()-14, self.main.flatsStep1View.height()-14, QtCore.Qt.KeepAspectRatio))
        self.main.flatsStep1View.setScene(scene)

    def updateZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled((self.main.flatsStep1Zoom.width()*2)-14, (self.main.flatsStep1Zoom.height()*2)-14, QtCore.Qt.KeepAspectRatio))
        self.main.flatsStep1Zoom.setScene(scene)

    def updateHistogram(self, hist):
        scene = QtWidgets.QGraphicsScene()

        # Determine the width and height of the scene
        width = self.main.objectStep1Hist.width() - 14
        height =  self.main.objectStep1Hist.height() - 14

        # Create a QGraphicsRectItem object for each histogram bar
        bar_width = width / len(hist)
        max_height = max(hist)
        for i, value in enumerate(hist):
            bar_height = height * value / max_height
            bar = QtWidgets.QGraphicsRectItem(i * bar_width, height - bar_height, bar_width, bar_height)
            scene.addItem(bar)

        self.main.objectStep1Hist.setScene(scene)
        
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
    finished = pyqtSignal()

    def run(self):
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[11]) #630 nm (red)
        self.main.camera_control.initialize_camera()
        i = 0
        for i in range(0,len(self.main.led_control.wavelength_list)):
            wavelength = self.main.led_control.wavelength_list[i]
            if self.cancelled:
                break
            self.wavelength.emit(wavelength)
            self.main.led_control.turn_on(wavelength)

            frame = self.main.camera_control.capture_at_exposure(self.main.camera_control.exposureArray[i])

            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
            self.sharedFrame.emit(img)
            
            histogram, bins = np.histogram(frame, bins=20, range=(0, 255))  # use 20 bins and a range of 0-255
            self.histogram.emit(histogram)
            debugpy.debug_this_thread()
            '''zoom = self.main.camera_control.zoom(frame,float(4.0))
            zImg = self.main.camera_control.convert_nparray_to_QPixmap(zoom)'''
            #zImg = img.scaled(img.size()*2)
            self.zoomedFrame.emit(img)
            self.main.cube_builder.add_flat_image(frame)
            self.main.cube_builder.subtract_flat(frame, i)
            #time.sleep(0.5) # 500 ms
            self.main.led_control.turn_off()
            self.progress.emit(i+1)
            i += 1
        self.main.camera_control.uninitialize_camera()
        self.main.led_control.turn_off()
        if not self.cancelled:
            self.finished.emit()
