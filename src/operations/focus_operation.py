from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class FocusOp(Operation):
    """
    """
    main = None

    def on_start(self):
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

    def cancel(self):
        ''' '''
        self.main.worker.notCancelled = False
        #self.main.thread.quit()
        self.main.led_control.turn_off()

    def finished(self):
        self.main.thread.quit()

    def updateFrame(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusView.width(), self.main.focusView.height(), QtCore.Qt.KeepAspectRatio))
        self.main.focusView.setScene(scene)

    def update2XZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusStep1Zoom1View.width()*2, self.main.focusStep1Zoom1View.height()*2, QtCore.Qt.KeepAspectRatio))
        self.main.focusStep1Zoom1View.setScene(scene)
        #self.main.focusStep1Zoom1View.scale(2,2)

    def update4XZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusStep1Zoom2View.width()*4, self.main.focusStep1Zoom2View.height()*4, QtCore.Qt.KeepAspectRatio))
        self.main.focusStep1Zoom2View.setScene(scene)
        #self.main.focusStep1Zoom2View.scale(4,4)

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
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[11]) #630 nm (red)
        # Initialize the camera
        self.main.camera_control.initialize_camera()
        while self.notCancelled:
            frame = self.main.camera_control.capture_at_exposure(self.main.camera_control.exposureArray[11])
            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
            '''x2 = self.main.camera_control.zoom(frame,float(4.0))
            x2Img = self.main.camera_control.convert_nparray_to_QPixmap(x2)
            x4 = self.main.camera_control.zoom(frame,float(8.0))
            x4Img = self.main.camera_control.convert_nparray_to_QPixmap(x4)'''
            '''copy = img.copy()
            x2Img = copy.scale(4,4)
            copy2 = copy.copy()
            x4Img = copy2.scale(8,8)'''
            self.mainFrame.emit(img)
            self.x2Frame.emit(img)
            self.x4Frame.emit(img)
            self.sharpness.emit(self.main.camera_control.get_sharpness())
            #time.sleep(0.5) # 500 ms
        self.main.camera_control.uninitialize_camera()
        self.finished.emit()