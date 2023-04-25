from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from skeleton.rectangle_selection import RectangleSelectView
import numpy as np

class EditOp(Operation):
    main = None

    def on_start(self):
        self.main.cropCancelButton.setEnabled(False)
        
    
    def updateEditView(self, img):
        scene = QtWidgets.QGraphicsScene()
        self.main.editView.setScene(scene)
        self.main.editView.setHidden(False)
        scene.addPixmap(img.scaled(self.main.editView.width(), self.main.editView.height(), QtCore.Qt.KeepAspectRatio))

    def rotate(self):
        self.main.cube_builder.rotate90(1)
        self.main.editDisplay(self.main.editComboBox.currentIndex())

    def crop(self):
        rectView = RectangleSelectView(self.main.editView.scene(), self.main.cube_builder.img_array[:,:,11])
        rectView.setZValue(1.0)
        self.main.editView.scene().addItem(rectView)
        # self.selectAreaButton.setProperty('visible', True)
        self.main.editView.setDragMode(QGraphicsView.NoDrag)
        self.main.cropButton.setText("Crop using Selection")
        self.main.cropButton.clicked.connect(lambda: self.getCropCoordinates(rectView))
        self.main.cropCancelButton.setEnabled(True)

    def getCropCoordinates(self, rectView):
        selectedArea = rectView.getSelectedArea()
        self.main.cube_builder.crop(selectedArea[0][1], selectedArea[1][1],
                                    selectedArea[0][0], selectedArea[1][0])
        frame = self.main.cube_builder.img_array[:,:,11]
        img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
        self.main.editDisplay(self.main.editComboBox.currentIndex())
        self.main.cropButton.setText("Start Crop")
        self.main.cropButton.clicked.connect(lambda: self.crop())
        self.main.cropCancelButton.setEnabled(False)

    def calibrate(self):
        rectView = RectangleSelectView(self.main.editView.scene(), self.main.cube_builder.img_array[:,:,11])
        rectView.setZValue(1.0)
        self.main.editView.scene().addItem(rectView)
        # self.selectAreaButton.setProperty('visible', True)
        self.main.editView.setDragMode(QGraphicsView.NoDrag)
        self.main.calibrationButton.clicked.connect(lambda: self.getCalibrationMask(rectView))
        self.main.calibrationButton.setText("Calibrate using Selection")

    def getCalibrationMask(self, rectView=RectangleSelectView):
        selectedArea = rectView.getSelectedArea()
        # Define progress 
        progress = QtWidgets.QProgressDialog("Calibrating Images...", "Cancel", 0, 8, self.main)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(True)
        progress.show()

        binaryImage = self.main.cube_builder.generateBinaryImage(selectedArea[0][1], selectedArea[1][1],
                                    selectedArea[0][0], selectedArea[1][0])
        if progress.wasCanceled():
                return
        
        # Update progress bar
        progress.setValue(1)
        QtWidgets.QApplication.processEvents()

        temps = self.main.cube_builder.final_array.astype(np.uint8) * binaryImage
        if progress.wasCanceled():
                return
        progress.setValue(2)
        QtWidgets.QApplication.processEvents()

        ones_sum = np.sum(binaryImage, axis = (0,1), where=(binaryImage != 0))
        if progress.wasCanceled():
                return
        progress.setValue(3)
        QtWidgets.QApplication.processEvents()

        meantemp = (np.sum(temps, axis=(0,1)) / ones_sum).astype(np.uint8)
        if progress.wasCanceled():
                return
        progress.setValue(4)
        QtWidgets.QApplication.processEvents()

        meantemp_cube = (np.broadcast_to(meantemp,self.main.cube_builder.final_array.shape)).astype(np.uint8)
        if progress.wasCanceled():
                return
        progress.setValue(5)
        QtWidgets.QApplication.processEvents()

        divided = (np.divide((self.main.cube_builder.final_array).astype(np.uint8),meantemp_cube,where=(meantemp_cube != 0),dtype=(np.float16)).astype(np.float16))
        if progress.wasCanceled():
                return
        progress.setValue(6)
        multiplied = (divided*255)
        if progress.wasCanceled():
                return
        progress.setValue(7)

        self.main.cube_builder.final_array = np.clip(multiplied, 0, 255).astype(np.uint8)
        if progress.wasCanceled():
                return
        progress.setValue(8)
        QtWidgets.QApplication.processEvents()
        self.main.editDisplay(self.main.editComboBox.currentIndex())
        self.main.calibrationButton.setEnabled(False)
        
        #self.main.cube_builder.calibrate(bImage, progress)

    def auto_calibrate(self):
        import numpy as np
        from PIL import Image, ImageOps
        from scipy import ndimage

        # Define threshold increment and maximum number of iterations
        thresh_increment = 0.05
        max_iterations = 20
        
        # Get the image array from self
        img_array = self.main.cube_builder.final_array
        
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
                return
        
        # Hide progress bar
        progress.hide()

        '''# Display the 11th image in the filtered image array as an example
        img = img_array_filt[:,:,11]
        img = ((img - np.min(img)) / (np.max(img) - np.min(img))) * 255
        img = img.astype(np.uint8)
        qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        scene = QtWidgets.QGraphicsScene()
        self.main.editView.setScene(scene)
        self.main.editView.setHidden(False)
        scene.addPixmap(pixmap.scaled(self.main.editView.width(), self.main.editView.height(), QtCore.Qt.KeepAspectRatio))'''

        # Replace the original image array with the filtered image array in self
        self.main.cube_builder.img_array = img_array_filt
        self.main.editDisplay(self.main.editComboBox.currentIndex())


    def finished(self):
        pass

    def cancel(self):
        self.main.cube_builder.revert_final()
        self.main.editDisplay(self.main.editComboBox.currentIndex())
