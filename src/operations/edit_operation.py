from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from skeleton.rectangle_selection import RectangleSelectView

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
        rectView = RectangleSelectView(self.main.editView.scene(), self.main.cube_builder.img_array[:,:,11])
        rectView.setZValue(1.0)
        self.main.editView.scene().addItem(rectView)
        # self.selectAreaButton.setProperty('visible', True)
        self.main.editView.setDragMode(QGraphicsView.NoDrag)
        self.main.selectionButton.clicked.connect(lambda: self.getCoordinates(rectView))

    def getCoordinates(self, rectView):
        selectedArea = rectView.getSelectedArea()
        self.main.cube_builder.crop(selectedArea[0][1], selectedArea[1][1],
                                    selectedArea[0][0], selectedArea[1][0])

    def auto_calibrate(self):
        import numpy as np
        from PIL import Image, ImageOps
        from scipy import ndimage

        # Define threshold increment and maximum number of iterations
        thresh_increment = 0.05
        max_iterations = 20

        # Get the image array from self
        img_array = self.main.cube_builder.img_array

        # Get the number of images and image dimensions
        num_images, height, width = img_array.shape

        # Initialize filtered image array
        img_array_filt = np.zeros_like(img_array)

        # Define progress 
        progress = QtWidgets.QProgressDialog("Auto-Calibrating Images...", "Cancel", 0, num_images, self.main)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(True)
        progress.show()

        # Define filter size
        filter_size = (int(height/10), int(width/10))

        # Process images in batches
        batch_size = 10
        for i in range(0, num_images, batch_size):
            # Get batch of images
            img_batch = img_array[i:i+batch_size]

            # Initialize filtered batch of images
            img_batch_filt = np.zeros_like(img_batch)

            # Filter and rescale each image individually
            for j in range(len(img_batch)):
                # Filter image
                img_filt = ndimage.convolve(img_batch[j], np.ones(filter_size)/(filter_size[0]*filter_size[1]), mode='reflect')

                # Rescale image
                p1, p99 = np.percentile(img_filt, (1, 99))
                img_filt = np.clip((img_filt - p1) / (p99 - p1), 0, 1)

                # Add filtered image to filtered batch of images
                img_batch_filt[j] = img_filt

            # Add filtered batch of images to filtered image array
            img_array_filt[i:i+batch_size] = img_batch_filt

            # Update progress bar
            progress.setValue(i+batch_size)
            QtWidgets.QApplication.processEvents()

            # Check for cancel
            if progress.wasCanceled():
                break

        # Hide progress bar
        progress.hide()

        # Display the 11th image in the filtered image array as an example
        img = img_array_filt[:,:,11]
        img = ((img - np.min(img)) / (np.max(img) - np.min(img))) * 255
        img = img.astype(np.uint8)
        qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        scene = QtWidgets.QGraphicsScene()
        self.main.editView.setScene(scene)
        self.main.editView.setHidden(False)
        scene.addPixmap(pixmap.scaled(self.main.editView.width(), self.main.editView.height(), QtCore.Qt.KeepAspectRatio))

        # Replace the original image array with the filtered image array in self
        self.main.cube_builder.img_array = img_array_filt

    def finished(self):
        pass

    def cancel(self):
        pass
