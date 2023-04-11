from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class EditOp(Operation):
    main = None

    def on_start(self):
        pass
    

    def rotate(self):
        self.main.cube_builder.rotate90(1)
        frame = self.main.cube_builder.img_array[:,:,11]
        img = self.main.camera_control.convert_nparray_to_QPixmap(frame)

        scene = QtWidgets.QGraphicsScene()
        self.main.editView.setScene(scene)
        self.main.editView.setHidden(False)
        scene.addPixmap(img.scaled(self.main.editView.width(), self.main.editView.height(), QtCore.Qt.KeepAspectRatio))

    def crop(self):
        pass

    def calibrate(self):
        pass


    def finished(self):
        pass

    def cancel(self):
        pass
