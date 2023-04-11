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



    def auto_calibrate(self):
        import numpy as np
        from PIL import Image, ImageOps
        from scipy import ndimage
        
        # load example image
        frame = self.main.cube_builder.img_array[:, :, 11]
        img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
        scene = QtWidgets.QGraphicsScene()
        self.main.editView.setScene(scene)
        self.main.editView.setHidden(False)
        scene.addPixmap(
            img.scaled(
                self.main.editView.width(),
                self.main.editView.height(),
                QtCore.Qt.KeepAspectRatio,
            )
        )

        # apply filter to each image
        H = np.ones([20, 20]) / 400
        img_array_filt = np.zeros_like(self.main.cube_builder.img_array)
        for i in range(self.main.cube_builder.img_array.shape[2]):
            img = Image.fromarray(self.main.cube_builder.img_array[:, :, i])
            img_filt = ndimage.convolve(img, H, mode="reflect")
            img_filt = Image.fromarray(img_filt)
            img_filt = ImageOps.equalize(img_filt)
            img_array_filt[:, :, i] = np.asarray(img_filt)

        # remove top 1% of data
        p1, p99 = np.percentile(img_array_filt, (1, 99))
        img_array_filt = np.clip(img_array_filt, p1, p99)
        img_array_filt = (img_array_filt - p1) / (p99 - p1)

        self.main.cube_builder.img_array = img_array_filt


    def finished(self):
        pass

    def cancel(self):
        pass
