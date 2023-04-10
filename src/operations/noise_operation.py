from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class NoiseOp(Operation):
    main = None
    img = None

    def on_start(self) -> None:
        self.main.noiseContinueButton.setEnabled(False)
        self.main.noiseRetakeButton.setEnabled(False)
        self.main.noiseView.setHidden(True)

        self.main.thread = QThread()
        self.main.worker = NoiseWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main

        self.main.thread.started.connect(self.main.worker.run)
        self.main.worker.imgView.connect(self.updateNoiseView)

        self.main.thread.start()

    def updateNoiseView(self, img):
        #self.img = newImg
        #img = self.main.camera_control.convert_nparray_to_QPixmap(newImg)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.noiseView.width(), self.main.noiseView.height(), QtCore.Qt.KeepAspectRatio))
        self.main.noiseView.setScene(scene)
        self.main.noiseView.setHidden(False)
    
    def finished(self):
        self.main.noiseContinueButton.setEnabled(True)
        self.main.noiseRetakeButton.setEnabled(True)
        self.main.thread.quit()


    def save(self):
        #self.main.noiseImg = self.img
        pass

    def cancel(self):
        self.main.thread.quit()

class NoiseWorker(QObject):
    imgView = pyqtSignal(QPixmap)
    main = None

    def run(self):
        self.main.camera_control.initialize_camera()
        frame = self.main.camera_control.capture()
        img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
        self.imgView.emit(img)
        self.main.camera_control.uninitialize_camera()
        self.main.cube_builder.add_noise_image(frame)
        self.main.noise_op.finished()