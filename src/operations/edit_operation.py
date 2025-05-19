import cv2
from operations.operation import Operation
from PyQt5 import QtCore, QtWidgets
from skimage import filters, morphology, measure
from PyQt5.QtWidgets import *
from skeleton.rectangle_selection import RectangleSelectView
import numpy as np
import colour
from scipy.interpolate import interp1d
from skeleton.Accessories import get_illuminant_spd_and_xyz
from skimage import exposure, color
import cv2

'''
Edit Operation for Editing Cube and Final Raw Images
Written by Sai Keshav Sasanapuri, Cecelia Ahrens, Eric Gao, and Robert Maron
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
        rectView = RectangleSelectView(self.main.editView.scene(), self.main.cube_builder.final_array[:,:,11])
        rectView.setZValue(1.0)
        self.main.editView.scene().addItem(rectView)
        self.main.editView.setDragMode(QGraphicsView.NoDrag)
        self.main.cropButton.setText("Crop using Selection")
        self.main.cropButton.clicked.disconnect()
        self.main.cropButton.clicked.connect(lambda: self.getCropCoordinates(rectView))

    '''Crops the cube based on provided rectView coordanates and connects cropButton to crop'''
    def getCropCoordinates(self, rectView):
        selectedArea = rectView.getSelectedArea()
        if selectedArea != [(0, 0), (0, 0)]  \
                and selectedArea[1][0] - selectedArea[0][0] > 1 \
                and selectedArea[1][1] - selectedArea[0][1] > 1:
            self.main.cube_builder.crop(selectedArea[0][1], selectedArea[1][1],
                                        selectedArea[0][0], selectedArea[1][0])
        self.main.editDisplay(self.main.editComboBox.currentIndex())
        self.main.cropButton.disconnect()
        self.main.cropButton.setText("Start Crop")
        self.main.cropButton.clicked.connect(lambda: self.crop())

    '''Starts rectangle selection for manual calibration and reconnects calibrationButton to get CalibrationMask'''
    def calibrate(self):
        self.main.performCalibration.disconnect()
        if not self.main.performCalibration.isEnabled():
            self.main.performCalibration.setEnabled(True)
        self.main.performCalibration.clicked.connect(lambda: self.getCalibrationMask(rectView))
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
            self.main.cube_builder.calibrate(self.main, binaryImage)
            self.generate_true_color_image(spectralon_coords=selectedArea)
            self.finished()
        else:
            self.main.calibrateCancel()

    '''Calibration without user selection'''

    def auto_calibrate(self):
        index = self.main.cube_builder.final_array.shape[2]//2
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
                    self.main.cube_builder.calibrate(self.main, bw_calibration_target),
                    self.generate_true_color_image(spectralon_coords=selectedArea),
                    self.finished()
                )
            )
            self.main.performCalibration.setEnabled(True)
            self.main.calibrationCancel.setEnabled(True)

        else:
            self.main.calibrationButton.setEnabled(True)
            self.main.autoButton.setEnabled(True)

    '''function to generate true color image'''
    
    def generate_true_color_image(self, spectralon_coords, illuminant='D65'):
        """
        Generate a white-balanced true-color image from a spectral image cube.

        Parameters:
            spectral_cube (np.ndarray): Spectral image cube with shape (16, H, W).
            band_centers (np.ndarray): Wavelengths corresponding to each spectral band (length 16).
            spectralon_coords (list): [(x1, y1), (x2, y2)] bounding box around the spectralon.
            illuminant (str): Standard illuminant to use ('D65' by default).

        Returns:
            np.ndarray: True-color image (H, W, 3), dtype float32, range [0, 1].
        """

        progress = QtWidgets.QProgressDialog("Generating true-color image", None, 0, 8, parent=self.main)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(True)
        progress.show()

        height, width, bands = self.main.cube_builder.img_array.shape
        
        if bands != 16:
            # Update progress bar
            progress.setValue(8)
            QtWidgets.QApplication.processEvents()
            return
        
        spectral_cube = np.copy(self.main.cube_builder.img_array)  # Now (H, W, 16)

        # Get standard illuminant and color matching functions
        std_wavelengths, illuminant_vals, cmfs_xyz = get_illuminant_spd_and_xyz(illuminant)

        # Update progress bar
        progress.setValue(1)
        QtWidgets.QApplication.processEvents()

        # Trim spectral bands to ~395–830 nm
        wl_min, wl_max = 395.0, 830.0
        band_centers = np.array(self.main.led_control.wavelength_list, dtype=np.float64)
        band_mask = (band_centers >= wl_min) & (band_centers <= wl_max)
        band_centers_trimmed = band_centers[band_mask]
        cube_trimmed = spectral_cube[:, :, band_mask] / 255.0  # Normalize reflectance

        # Update progress bar
        progress.setValue(2)
        QtWidgets.QApplication.processEvents()

        # Interpolate illuminant and CMFs
        illum_interp = interp1d(std_wavelengths, illuminant_vals, kind='linear', fill_value="extrapolate")(
            band_centers_trimmed)
        x = interp1d(std_wavelengths, cmfs_xyz[:, 0], kind='linear', fill_value='extrapolate')(band_centers_trimmed)
        y = interp1d(std_wavelengths, cmfs_xyz[:, 1], kind='linear', fill_value='extrapolate')(band_centers_trimmed)
        z = interp1d(std_wavelengths, cmfs_xyz[:, 2], kind='linear', fill_value='extrapolate')(band_centers_trimmed)
        xyz_interp = np.column_stack((x, y, z))

        # Update progress bar
        progress.setValue(4)
        QtWidgets.QApplication.processEvents()

        # Flatten the image for matrix multiplication
        flat = cube_trimmed.reshape(-1, cube_trimmed.shape[2]).T  # (bands, H*W)
        XYZ = xyz_interp.T @ np.diag(illum_interp) @ flat  # (3, H*W)
        XYZ_image = XYZ.T.reshape(height, width, 3)
        XYZ_image = (XYZ_image - XYZ_image.min()) / (XYZ_image.max() - XYZ_image.min())

        # Update progress bar
        progress.setValue(7)
        QtWidgets.QApplication.processEvents()

        # Convert to sRGB
        sRGB = colour.XYZ_to_sRGB(XYZ_image)
        sRGB = np.clip(sRGB, 0, 1)

        # Extract spectralon region
        (x1, y1), (x2, y2) = spectralon_coords
        white_patch = sRGB[y1:y2, x1:x2, :]
        avg_white = np.mean(white_patch.reshape(-1, 3), axis=0)

        # Apply white balancing
        true_white = np.array([243.0, 243.0, 242.0]) / 255.0
        scale_factors = true_white / avg_white
        balanced = np.clip(sRGB * scale_factors, 0, 1)

        # rgb_img = (balanced * 255).clip(0, 255).astype(np.uint8)
        self.main.cube_builder.bgr_img = (balanced * 255).clip(0, 255).astype(np.uint8)
        # self.main.cube_builder.bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)

        # Update progress bar
        progress.setValue(8)
        QtWidgets.QApplication.processEvents()

    def finished(self):
        self.main.editDisplay(self.main.editComboBox.currentIndex())
        self.main.autoButton.setEnabled(False)
        self.main.calibrationButton.setEnabled(False)
        self.main.calibrationCancel.setEnabled(False)
        self.main.performCalibration.setEnabled(False)

    '''Cancel and revert edits'''
    def cancel(self):
        self.main.editDisplay(self.main.editComboBox.currentIndex())
