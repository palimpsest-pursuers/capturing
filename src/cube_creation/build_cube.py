import os
import numpy as np
import spectral.io.envi as envi
import scipy.ndimage as ndimage
from tifffile import imwrite
from PyQt5 import QtCore, QtWidgets

'''
Cube Builder for Storing Images, Image Math, Building the Final Cube, and Saving Images
Written by Sai Keshav Sasanapuri, Cecelia Ahrens, Mallory Bridge
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
    bgr_img = []

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
        self.wavelengths.append(wavelength)

    '''Adds raw flats image ("img") to "flats_array" '''

    def add_flat_image(self, img):
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

    def apply_flats(self, UI):
        if len(self.flats_array) == 0:
            self.revert_final(UI)
        elif self.flats_array.shape[2] == self.final_array.shape[2]:
            # Define progress
            progress = QtWidgets.QProgressDialog("Dividing with flat-field images", "Cancel", 0,
                                                 self.final_array.shape[2], parent=UI)
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
                    self.revert_final(UI)
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
            progress.setValue(self.final_array.shape[2])
            QtWidgets.QApplication.processEvents()

    '''Sets noise image "noise" to "img"'''

    def add_noise_image(self, img):
        self.noise = img

    '''Rotates all image arrays 90 degrees "rotations" number of times'''

    def rotate90(self, rotations):
        self.final_array = np.rot90(self.final_array, rotations, (0, 1))

    '''Crops all image array to the given coordiantes'''

    def crop(self, x1, x2, y1, y2):
        self.final_array = self.final_array[x1:x2, y1:y2, :]

    '''Generates a binary image where all values in the provided coordiates are 1 and everything else is 0'''

    def generateBinaryImage(self, x1, x2, y1, y2):
        zeros = np.zeros(self.final_array.shape)
        zeros[x1:x2, y1:y2, :] = 1.0
        return zeros

    '''Calibrate the final image using "binaryImage"'''

    def calibrate(self, UI, binaryImage):
        """
        temps = self.final_array.astype(float) * binaryImage
        cnt2 = np.sum(binaryImage[binaryImage != 0])
        mean_temps = [np.mean(temps[:,:,i][binaryImage != 0]) for i in range(self.final_array.shape[2])]
        dataCube = self.final_array.astype(float) / np.array(mean_temps)[None, None, :]
        dataCube[dataCube > 1] = 1
        self.final_cube = dataCube
        """
        # Define progress
        progress = QtWidgets.QProgressDialog("Calibrating Images...", None, 0, 8, parent=UI)
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
        return out

    '''Revert flat subraction and calibration'''

    def revert_final(self, UI):
        # Define progress
        progress = QtWidgets.QProgressDialog("Reverting Flat-Fields", "Cancel", 0, 1, parent=UI)
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

    '''Build final cube and save it and all raw images to "destination" using "name"'''

    def build(self, destination, name):
        # for envi header file
        self.samples = self.final_array.shape[1]
        self.lines = self.final_array.shape[0]
        self.bands = self.final_array.shape[2]
        # save cube
        try:
            envi.save_image(destination + "\\" + name + ".hdr", self.final_array,
                            dtype=self.final_array.dtype, interleave=self.interleave, ext=None,
                            byteorder=self.byte_order, metadata=self.create_metadata(), force=True)
            # self.img_array = []
            rawPath = os.path.join(destination, name + " Raw Images")
            os.makedirs(rawPath)
        except Exception as ex:
            return ("Image cube with this name already exists in this folder.\n"
                    + "Please delete cube with the same name or choose a different folder.\n")

        # save all raw object images as individual tiffs in its own subdirectory
        w = 0
        for x in range(0, len(self.wavelengths)):
            img = np.copy(self.img_array)[:, :, w]
            imwrite(rawPath + "\\" + name + "-" + self.wavelengths[w] + ".tif", img, shape=(img.shape))
            w = w + 1

        if len(self.flats_array) > 0 and self.img_array.shape == self.flats_array.shape:
            # save all raw flats images as individual tiffs in its own subdirectory
            flatsPath = os.path.join(destination, name + "Flat Images")
            os.makedirs(flatsPath)

            w = 0
            for x in range(0, len(self.wavelengths)):
                flat = np.copy(self.flats_array)[:, :, w]
                imwrite(flatsPath + "\\" + name + "-" + self.wavelengths[w] + ".tif", flat, shape=(img.shape))
                w = w + 1
        if len(self.noise) > 0:
            # save noise image
            imwrite(destination + "\\" + name + "-noise.tif", self.noise, shape=(self.noise.shape))

        if len(self.bgr_img) > 0:
            # save noise image
            imwrite(destination + "\\" + name + "-true_color.tif", self.bgr_img, shape=(self.bgr_img.shape))
        return "Files Saved Successfully"

    '''Create Envi header file metadata'''

    def create_metadata(self):
        return {"wavelength": self.get_wavelength_str(),
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
        for x in range(1, len(self.wavelengths)+1):
            if x != 1:
                final = final + ','
            final = final + 'band' + str(x) + ': (' + str(self.wavelengths[x-1] + ')')
        final = final + '}'
        return final

    '''ready for redoing image capture'''

    def re_capture(self):
        self.img_array = []
        self.final_array = []
        self.flats_array = []
        self.noise = []
        self.wavelengths = []
