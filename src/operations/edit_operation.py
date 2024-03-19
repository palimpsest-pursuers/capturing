import cv2
from operations.operation import Operation
from PyQt5 import QtCore, QtWidgets
from skimage import filters, morphology, measure
from PyQt5.QtWidgets import *
from skeleton.rectangle_selection import RectangleSelectView
import numpy as np

'''
Edit Operation for Editing Cube and Final Raw Images
Written by Cecelia Ahrens, Eric Gao, and Robert Maron
'''
class EditOp(Operation):
    main = None

    '''Ensures correct starting state'''
    def on_start(self):
        self.main.autoButton.setEnabled(True)
        self.main.calibrationButton.setEnabled(True)
        self.main.calibrationCancel.setEnabled(False)
        self.main.performCalibration.setEnabled(False)
        
    '''Update Main Display'''
    def updateEditView(self, img):
        scene = QtWidgets.QGraphicsScene()
        self.main.editView.setScene(scene)
        self.main.editView.setHidden(False)
        scene.addPixmap(img.scaled(self.main.editView.width(), self.main.editView.height(), QtCore.Qt.KeepAspectRatio))

    '''Rotates cube and updates display'''
    def rotate(self):
        self.main.cube_builder.rotate90(1)
        self.main.editDisplay(self.main.editComboBox.currentIndex())

    '''Starts rectangle selection and connects cropButton to getCropCoodinates'''
    def crop(self):
        rectView = RectangleSelectView(self.main.editView.scene(), self.main.cube_builder.img_array[:,:,11])
        rectView.setZValue(1.0)
        self.main.editView.scene().addItem(rectView)
        self.main.editView.setDragMode(QGraphicsView.NoDrag)
        self.main.cropButton.setText("Crop using Selection")
        self.main.cropButton.clicked.disconnect()
        self.main.cropButton.clicked.connect(lambda: self.getCropCoordinates(rectView))

    '''Crops the cube based on provided rectView coordanates and connects cropButton to crop'''
    def getCropCoordinates(self, rectView):
        selectedArea = rectView.getSelectedArea()
        if selectedArea != [(0, 0), (0, 0)] and selectedArea[0] != selectedArea[1]:
            self.main.cube_builder.crop(selectedArea[0][1], selectedArea[1][1],
                                        selectedArea[0][0], selectedArea[1][0])
            frame = self.main.cube_builder.img_array[:,:,11]
            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
        self.main.editDisplay(self.main.editComboBox.currentIndex())
        self.main.cropButton.disconnect()
        self.main.cropButton.setText("Start Crop")
        self.main.cropButton.clicked.connect(lambda: self.crop())

    '''Starts rectangle selection for manual calibration and reconnects calibrationButton to get CalibrationMask'''
    def calibrate(self):
        self.main.performCalibration.disconnect()
        self.main.performCalibration.clicked.connect(
            lambda: (
                self.getCalibrationMask(rectView),
                self.finished()
            )
        )
        rectView = RectangleSelectView(self.main.editView.scene(), self.main.cube_builder.img_array[:,:,11])
        rectView.setZValue(1.0)
        self.main.editView.scene().addItem(rectView)
        self.main.editView.setDragMode(QGraphicsView.NoDrag)

    '''Starts Manual calibration based on rectView and with a progress Dialog'''

    def getCalibrationMask(self, rectView=RectangleSelectView):
        self.main.calibrationButton.setEnabled(False)
        selectedArea = rectView.getSelectedArea()
        if selectedArea != [(0, 0), (0, 0)] and selectedArea[0] != selectedArea[1]:

            # create binary image mask based on rectView
            binaryImage = self.main.cube_builder.generateBinaryImage(selectedArea[0][1], selectedArea[1][1],
                                                                     selectedArea[0][0], selectedArea[1][0])
            self.main.cube_builder.calibrate(binaryImage)

    '''Calibration without user selection'''

    def auto_calibrate(self):
        # index = len(self.main.cube_builder.final_array.shape[2])//2
        index = 8
        self.main.editDisplay(index)
        img = np.copy(self.main.cube_builder.final_array[:, :, index])

        # Filter out any spots on the calibration target
        img_filt = cv2.blur(img, (20, 20)) / 400

        # Remove top 1% of data
        out = np.clip(img_filt, 0, np.percentile(img_filt, 99))

        cnt = 0
        stats = None

        # Set start threshold
        thresh = np.median(out)
        while (stats is None) and (cnt < 20) and (thresh < 1):
            cnt += 1
            bw = img_filt >= (1 - thresh)
            labeled_bw = morphology.label(bw)
            regions = measure.regionprops(labeled_bw)

            # Select the largest region if any
            if regions:
                stats = max(regions, key=lambda x: x.area)
                break  # Exit the loop once the largest region is found

            thresh += 0.05

        if stats is not None:
            selem = morphology.square(30)
            bw_calibration_target = morphology.binary_erosion(bw, selem)
        else:
            bw_calibration_target = np.zeros_like(bw, dtype=bool)

        bw_calibration_target = bw_calibration_target.astype(int)

        if len(bw_calibration_target) > 1:
            # Create an RGB copy of the grayscale image
            rgb_img = np.stack((img,) * 3, axis=-1)

            # Set the red channel to 1 where the filter area is detected
            rgb_img[bw_calibration_target == 1, 0] = 1
            bw_calibration_target = np.expand_dims(bw_calibration_target, axis=-1)
            # Use broadcasting to replicate the binary image across all 16 channels
            bw_calibration_target = np.broadcast_to(bw_calibration_target, img.shape + (16,))
            img = self.main.camera_control.convert_nparray_to_QPixmap(rgb_img)
            self.main.edit_op.updateEditView(img)
            self.main.performCalibration.disconnect()
            self.main.performCalibration.clicked.connect(
                lambda: (
                    self.main.cube_builder.calibrate(bw_calibration_target),
                    self.finished()
                )
            )
            self.main.performCalibration.setEnabled(True)
            self.main.calibrationCancel.setEnabled(True)

        else:
            self.main.calibrationButton.setEnabled(True)
            self.main.autoButton.setEnabled(True)

    def finished(self):
        self.main.editDisplay(self.main.editComboBox.currentIndex())
        self.main.autoButton.setEnabled(False)
        self.main.calibrationButton.setEnabled(False)
        self.main.calibrationCancel.setEnabled(False)
        self.main.performCalibration.setEnabled(False)

    '''Cancel and revert edits'''
    def cancel(self):
        # self.main.cube_builder.revert_final()
        self.main.editDisplay(self.main.editComboBox.currentIndex())
