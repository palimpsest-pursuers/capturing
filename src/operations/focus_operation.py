from operations.operation import Operation
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

'''
Focus Operation for Displaying "Live" Images for Camara Focus Adjustment
Written by Cecelia Ahrens
'''
class FocusOp(Operation):
    main = None

    def on_start(self):
        #start thread, move worker to thread
        self.main.thread = QThread()
        self.main.worker = FocusWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main

        #connect slots
        self.main.thread.started.connect(self.main.worker.run)
        self.main.worker.mainFrame.connect(self.updateFrame)
        self.main.worker.x2Frame.connect(self.update2XZoomed)
        self.main.worker.x4Frame.connect(self.update4XZoomed)
        self.main.worker.sharpness.connect(self.updateSharpness)
        self.main.worker.finished.connect(self.finished)

        self.main.thread.start()

    '''Cancel Operation'''
    def cancel(self):
        self.main.worker.notCancelled = False
        self.main.led_control.turn_off()

    '''Finish Operation'''
    def finished(self):
        self.main.thread.quit()

    '''Update Main Display'''
    def updateFrame(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusView.width(), self.main.focusView.height(), QtCore.Qt.KeepAspectRatio))
        self.main.focusView.setScene(scene)

    '''Update smaller display for X2 zoomed image'''
    def update2XZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusStep1Zoom1View.width()*2, self.main.focusStep1Zoom1View.height()*2, QtCore.Qt.KeepAspectRatio))
        self.main.focusStep1Zoom1View.setScene(scene)

    '''Update smaller display for X2 zoomed image'''
    def update4XZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusStep1Zoom2View.width()*4, self.main.focusStep1Zoom2View.height()*4, QtCore.Qt.KeepAspectRatio))
        self.main.focusStep1Zoom2View.setScene(scene)

    '''Update sharpness label'''
    def updateSharpness(self, n):
        self.main.focusStep1Sharpness.setText(f"Sharpness: {n}")
    
class FocusWorker(QObject):
    mainFrame = pyqtSignal(QPixmap)
    x2Frame = pyqtSignal(QPixmap)
    x4Frame = pyqtSignal(QPixmap)
    sharpness = pyqtSignal(int)
    notCancelled = True
    main = None
    finished = pyqtSignal()

    def run(self):
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[8])
        # Initialize the camera
        self.main.camera_control.initialize_camera()
        while self.notCancelled:
            frame = self.main.camera_control.capture_at_exposure(self.main.camera_control.exposureArray[8], 8)
            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
            self.mainFrame.emit(img)
            self.x2Frame.emit(img)
            self.x4Frame.emit(img)
            self.sharpness.emit(self.main.camera_control.get_sharpness())
        self.main.camera_control.uninitialize_camera()
        self.finished.emit()