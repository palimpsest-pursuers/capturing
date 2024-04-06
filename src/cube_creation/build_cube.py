import os
import numpy as np
import spectral.io.envi as envi
import scipy.ndimage as ndimage
from tifffile import imwrite
from PyQt5 import QtCore, QtWidgets
# from scipy.interpolate import interp1d
# from skimage.color import lab2rgb

'''
Cube Builder for Storing Images, Image Math, Building the Final Cube, and Saving Images
Written by Cecelia Ahrens, and Mallory Bridge, Sai Keshav Sasanapuri
'''


class CubeBuilder():
    img_array = []  # All the raw object images
    flats_array = []
    final_array = []
    noise = []
    destination_dir = ""
    filenames = None
    wavelengths = []
    description = '{Saved by MISHA Capturing (Python) App}'
    samples = None
    lines = None
    bands = None
    header_offset = 0
    file_type = 'ENVI Standard'
    data_type = 4
    interleave = 'bsq'
    sensor_type = 'Unknown'
    byte_order = 0

    '''Adds raw object image ("img") to "img_array" and appends its wavelength to the list'''

    def add_raw_image(self, img, wavelength):
        if len(self.img_array) == 0:
            self.wavelengths = []
            self.img_array = img
            if len(self.noise) > 0:
                self.final_array = np.subtract(img, self.noise)
            else:
                self.final_array = img
        else:
            self.img_array = np.dstack((self.img_array, img))
            if len(self.noise) > 0:
                sub = np.subtract(img, self.noise)
                self.final_array = np.dstack((self.final_array, sub))
            else:
                self.final_array = np.dstack((self.final_array, img))
        print(self.final_array.shape)
        self.wavelengths.append(wavelength)

    '''Adds raw flats image ("img") to "flats_array" '''

    def add_flat_image(self, img):
        print('flats', img.shape)
        if len(self.flats_array) == 0:
            self.flats_array = img
        else:
            self.flats_array = np.dstack((self.flats_array, img))

    '''Subtracts flat image "img" from image in "final_array" at dimension "index" and updates "final_array" '''

    def subtract_flat(self, img, index):
        # nWhite = np.divide(np.subtract(img,np.min(img)), np.subtract(np.max(img),np.min(img)))
        filtered = ndimage.gaussian_filter(img, 20)
        copy = np.copy(self.final_array[:, :, index])
        divided = np.divide(copy, filtered, where=(filtered != 0))

        # normalize this thing so we get stuff on a 0-1 scale
        divided = ((divided - np.min(divided)) / (np.max(divided) - np.min(divided)))

        # convert the divided values into 255 uint8
        self.final_array[:, :, index] = (divided * 255).astype(np.uint8)

    '''Subtracts all flat images "img" from images in "final_array" '''

    def apply_flats(self):
        if len(self.flats_array) == 0:
            self.revert_final()
        elif self.flats_array.shape[2] == self.final_array.shape[2]:
            # Define progress
            progress = QtWidgets.QProgressDialog("Dividing with flat-field images", "Cancel", 0, self.final_array.shape[2])
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setAutoReset(True)
            progress.show()

            if progress.wasCanceled():
                return

            # Update progress bar
            progress.setValue(1)
            QtWidgets.QApplication.processEvents()

            for index in range(self.final_array.shape[2]):

                if progress.wasCanceled():
                    self.revert_final()
                    return
                progress.setValue(index)
                QtWidgets.QApplication.processEvents()

                filtered = ndimage.gaussian_filter(self.flats_array[:, :, index], 20)
                copy = np.copy(self.final_array[:, :, index])
                divided = np.divide(copy, filtered, where=(filtered != 0))

                # normalize this thing, so we get stuff on a 0-1 scale
                divided = ((divided - np.min(divided)) / (np.max(divided) - np.min(divided)))

                # convert the divided values into 255 uint8
                self.final_array[:, :, index] = (divided * 255).astype(np.uint8)

    '''Sets noise image "noise" to "img"'''

    def add_noise_image(self, img):
        self.noise = img

    '''Rotates all image arrays 90 degrees "rotations" number of times'''

    def rotate90(self, rotations):
        self.final_array = np.rot90(self.final_array, rotations, (0, 1))

    '''Crops all image array to the given coordiantes'''

    def crop(self, x1, x2, y1, y2):
        self.final_array = self.final_array[x1:x2, y1:y2, :]
        print("done")

    '''Generates a binary image where all values in the provided coordiates are 1 and everything else is 0'''

    def generateBinaryImage(self, x1, x2, y1, y2):
        zeros = np.zeros(self.final_array.shape)
        zeros[x1:x2, y1:y2, :] = 1.0
        return zeros

    '''Calibrate the final image using "binaryImage"'''

    def calibrate(self, binaryImage):
        """
        temps = self.final_array.astype(float) * binaryImage
        cnt2 = np.sum(binaryImage[binaryImage != 0])
        mean_temps = [np.mean(temps[:,:,i][binaryImage != 0]) for i in range(self.final_array.shape[2])]
        dataCube = self.final_array.astype(float) / np.array(mean_temps)[None, None, :]
        dataCube[dataCube > 1] = 1
        self.final_cube = dataCube
        """
        # Define progress
        progress = QtWidgets.QProgressDialog("Calibrating Images...", "Cancel", 0, 8)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(True)
        progress.show()

        if progress.wasCanceled():
            return

        # Update progress bar
        progress.setValue(1)
        QtWidgets.QApplication.processEvents()

        # CALIBRATION MATH

        temps = self.final_array.astype(np.uint8) * binaryImage
        if progress.wasCanceled():
            return
        progress.setValue(2)
        QtWidgets.QApplication.processEvents()

        ones_sum = np.sum(binaryImage, axis=(0, 1), where=(binaryImage != 0))
        if progress.wasCanceled():
            return
        progress.setValue(3)
        QtWidgets.QApplication.processEvents()

        meantemp = (np.sum(temps, axis=(0, 1)) / ones_sum).astype(np.uint8)
        if progress.wasCanceled():
            return
        progress.setValue(4)
        QtWidgets.QApplication.processEvents()

        meantemp_cube = (np.broadcast_to(meantemp, self.final_array.shape)).astype(np.uint8)
        if progress.wasCanceled():
            return
        progress.setValue(5)
        QtWidgets.QApplication.processEvents()

        divided = (
            np.divide(self.final_array.astype(np.uint8), meantemp_cube, where=(meantemp_cube != 0),
                      dtype=np.float16).astype(np.float16))
        if progress.wasCanceled():
            return
        progress.setValue(6)
        multiplied = (divided * 255)
        if progress.wasCanceled():
            return
        progress.setValue(7)

        self.final_array = np.clip(multiplied, 0, 255).astype(np.uint8)
        if progress.wasCanceled():
            return
        progress.setValue(8)
        QtWidgets.QApplication.processEvents()

    def auto_calibrate(self, img):
        pass

    '''incomplete'''

    def stretch_image(self, percent):
        out = np.empty_like(self.img_array)

        for i in range(0, self.img_array.shape[2]):
            band = self.img_array[:, :, i]
            tempSorted = band.sort(1)
        return out

    '''Revert flat subraction and calibration'''

    def revert_final(self):
        print("entered here")
        # Define progress
        progress = QtWidgets.QProgressDialog("Reverting Flat-Fields", "Cancel", 0, 1)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(True)
        progress.show()

        if progress.wasCanceled():
            return

        # Update progress bar
        progress.setValue(1)
        QtWidgets.QApplication.processEvents()
        self.final_array = self.img_array.copy()
        if len(self.noise) > 0:
            for x in range(0, len(self.wavelengths)):
                img = self.img_array[:, :, x].copy()
                self.final_array[:, :, x] = np.subtract(img, self.noise)

        # Update progress bar
        progress.setValue(1)
        QtWidgets.QApplication.processEvents()
        print("image", self.img_array.shape)
        print("final", self.final_array.shape)

    # def true_color(self):
    #     data_cube = np.copy(self.final_array)
    #     row, col, bands = data_cube.shape
    #
    #     data = data_cube.reshape(row * col, bands)
    #
    #     try:
    #         wave = np.copy(self.wavelengths)
    #     except:
    #         pass
    #
    #     # read in illuminants (300 - 830)
    #     illum = np.loadtxt('Wave_A_D50_D55_D65_D75.csv', delimiter=',')
    #     illum_wave = illum[:, 0]
    #     illum_D65 = illum[:, 4]
    #
    #     # read XYZ observer (360 - 830)
    #     observer2deg = np.loadtxt('ObserverXYZ.csv', delimiter=',')
    #
    #     # interp all data to object wavelengths
    #     illum_D65_interp = interp1d(illum_wave, illum_D65, kind='linear')(wave)
    #     observer2deg_x_interp = interp1d(observer2deg[:, 0], observer2deg[:, 1], kind='linear')(wave)
    #     observer2deg_y_interp = interp1d(observer2deg[:, 0], observer2deg[:, 2], kind='linear')(wave)
    #     observer2deg_z_interp = interp1d(observer2deg[:, 0], observer2deg[:, 3], kind='linear')(wave)
    #
    #     # calculate the CIE XYZ tristimulus value
    #     num = data.shape[0]
    #     D65_rep = np.tile(illum_D65_interp, (num, 1)).T
    #
    #     object_ave = (data / 100).T
    #     X = 100 * np.nansum(D65_rep * object_ave * np.tile(observer2deg_x_interp, (num, 1)), axis=0) / np.nansum(
    #         D65_rep * np.tile(observer2deg_y_interp, (num, 1)), axis=0)
    #     Y = 100 * np.nansum(D65_rep * object_ave * np.tile(observer2deg_y_interp, (num, 1)), axis=0) / np.nansum(
    #         D65_rep * np.tile(observer2deg_y_interp, (num, 1)), axis=0)
    #     Z = 100 * np.nansum(D65_rep * object_ave * np.tile(observer2deg_z_interp, (num, 1)), axis=0) / np.nansum(
    #         D65_rep * np.tile(observer2deg_y_interp, (num, 1)), axis=0)
    #
    #     # convert XYZ to LAB
    #     Xn, Yn, Zn = 95.04, 100.0, 108.88
    #
    #     x = X / Xn
    #     x_Y_larger = np.power(x, 1 / 3)
    #     x_Y_smaller = 7.787 * x + 16 / 116
    #     x_Y = np.zeros_like(x)
    #     x_Y[x > 0.00856] = x_Y_larger[x > 0.00856]
    #     x_Y[x <= 0.00856] = x_Y_smaller[x <= 0.00856]
    #     L = 116 * x_Y - 16
    #
    #     x = X / Xn
    #     x_X_larger = np.power(x, 1 / 3)
    #     x_X_smaller = 7.787 * x + 16 / 116
    #     x_X = np.zeros_like(x)
    #     x_X[x > 0.00856] = x_X_larger[x > 0.00856]
    #     x_X[x <= 0.00856] = x_X_smaller[x <= 0.00856]
    #     a = 500 * (x_X - x_Y)
    #
    #     x = Z / Zn
    #     x_Z_larger = np.power(x, 1 / 3)
    #     x_Z_smaller = 7.787 * x + 16 / 116
    #     x_Z = np.zeros_like(x)
    #     x_Z[x > 0.00856] = x_Z_larger[x > 0.00856]
    #     x_Z[x <= 0.00856] = x_Z_smaller[x <= 0.00856]
    #     b = 200 * (x_Y - x_Z)
    #
    #     LAB = np.vstack((L, a, b)).T
    #
    #     # convert LAB to RGB
    #     RGB = lab2rgb(LAB.reshape(row, col, 3))
    #
    #     # normalize RGB values
    #     R = RGB[:, :, 0]
    #     G = RGB[:, :, 1]
    #     B = RGB[:, :, 2]
    #     RGB[:, :, 0] = (R - np.min(R)) / (np.max(R) - np.min(R))
    #     RGB[:, :, 1] = (G - np.min(G)) / (np.max(G) - np.min(G))
    #     RGB[:, :, 2] = (B - np.min(B)) / (np.max(B) - np.min(B))
    #
    #     bands = ['Red', 'Green', 'Blue']
    #
    #     return RGB, bands

    '''Build final cube and save it and all raw images to "destanation" using "name"'''

    def build(self, destanation, name):
        # for envi header file
        self.samples = self.final_array.shape[1]
        self.lines = self.final_array.shape[0]
        self.bands = self.final_array.shape[2]
        print(self.samples, self.lines, self.bands)
        # save cube
        try:
            envi.save_image(destanation + "\\" + name + ".hdr", self.final_array,
                            dtype=self.final_array.dtype, interleave=self.interleave, ext=None,
                            byteorder=self.byte_order, metadata=self.create_metadata())
            # self.img_array = []
            rawPath = os.path.join(destanation, name + " Raw Images")
            os.makedirs(rawPath)
        except Exception as ex:
            print(ex)
            return ("Image cube with this name already exists in this folder.\n"
                    + "Please delete cube with the same name or choose a diffrent folder.\n")

        # save all raw object images as individual tiffs in its own subdirectory
        w = 0
        for x in range(0, len(self.wavelengths)):
            img = np.copy(self.img_array)[:, :, w]
            imwrite(rawPath + "\\" + name + "-" + self.wavelengths[w] + ".tif", img, shape=(img.shape))
            w = w + 1

        if len(self.flats_array) > 0 and self.img_array.shape == self.flats_array.shape:
            # save all raw flats images as individual tiffs in its own subdirectory
            flatsPath = os.path.join(destanation, name + "Flat Images")
            os.makedirs(flatsPath)

            w = 0
            for x in range(0, len(self.wavelengths)):
                flat = np.copy(self.flats_array)[:, :, w]
                imwrite(flatsPath + "\\" + name + "-" + self.wavelengths[w] + ".tif", flat, shape=(img.shape))
                w = w + 1
        if len(self.noise) > 0:
            # save noise image
            imwrite(destanation + "\\" + name + "-noise.tif", self.noise, shape=(self.noise.shape))
        return

    '''Create Envi header file metadata'''

    def create_metadata(self):
        return {"wavelengths": self.get_wavelength_str(),
                "description": self.description,
                "samples": self.samples,
                "lines": self.lines,
                "bands": self.bands,
                "header offset": self.header_offset,
                "file type": self.file_type,
                "data type": self.data_type,
                "interleave": self.interleave,
                "sensor type": self.sensor_type,
                "byte order": self.byte_order,
                "band names": self.get_bandnames_str()}

    '''Get wavelength list as a string'''

    def get_wavelength_str(self):
        final = '{'
        for x in range(0, len(self.wavelengths)):
            if x != 0:
                final = final + ','
            final = final + str(self.wavelengths[x])
        final = final + '}'
        return final

    '''Get bandnames as a string'''

    def get_bandnames_str(self):
        final = '{'
        for x in range(0, len(self.wavelengths)):
            if x != 0:
                final = final + ','
            final = final + 'band' + str(x-1) + ': (' + str(self.wavelengths[x] + ')')
        final = final + '}'
        return final

    '''ready for redoing image capture'''
    def re_capture(self):
        self.img_array = []
        self.final_array = []
        self.flats_array = []
        self.noise = []
        self.wavelengths = []


