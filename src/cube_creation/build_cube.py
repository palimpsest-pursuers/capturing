#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
from PIL import Image
import spectral.io.envi as envi
import scipy.ndimage as ndimage


class CubeBuilder():
    img_array = []
    flats_array = None
    noise = None
    destination_dir = ""
    filenames = None
    wavelengths = []
    description = '{Saved by Spectral Analysis App}'
    samples = None
    lines = None
    bands = None
    header_offset = 0
    file_type = 'ENVI Standard'
    data_type = 4
    interleave = 'bsq'
    sensor_type = 'Unknown'
    byte_order = 0

    
    '''def __init__(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        #dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("Images (*.tiff)")
        
        self.filenames = dlg.getOpenFileNames(None,"Select captured images",'',"Images (*.tiff)",)[0]
        self.build()'''
        
    def add_raw_image(self, img, wavelength):
        #print(img.shape)
        if (self.img_array == []):
            self.img_array = img
        else:
            self.img_array = np.dstack((self.img_array,img))
        #print(self.img_array.shape)
        self.wavelengths.append(wavelength)

    def add_flat_image(self, img):
        if (self.flats_array == []):
            self.flats_array = img
        else:
            self.flats_array = np.dstack((self.flats_array,img))

    def subtract_flats(self, img, index):
        filtered = ndimage.gaussian_filter(img, 20)
        copy = np.copy(self.img_array[:,:,index])
        divided = copy / filtered
        self.img_array[:,:,index] = divided

    def add_noise_image(self, img):
        self.noise = img

    def rotate90(self, rotations):
        self.img_array = np.rot90(self.img_array, rotations, (0,1))

    def crop(self, x1, x2, y1, y2):
        self.img_array = self.img_array[x1:x2, y1:y2, : ]

    def calibrate(self, binaryImage):
        temp = self.img_array * binaryImage
        cnt2 = np.sum(binaryImage[binaryImage != 0])
        meantemp = np.sum(temp) / cnt2
        meantemparray = np.tile(meantemp, (self.img_array.shape[0], self.img_array.shape[1]))
        datacube = self.img_array / meantemparray
        datacube[datacube > 1] = 1
        self.img_array = datacube

    def auto_calibrate(self, img):
        pass

    def stretch_image(self, percent):
        out = np.empty_like(self.img_array)

        for i in range(0,self.img_array.shape[2]):
            band = self.img_array[:,:,i]
            tempSorted = band.sort(1)
        return out

    def build(self, destanation, name):
        
        self.samples = self.img_array.shape[1]
        self.lines = self.img_array.shape[0]
        self.bands = self.img_array.shape[2]

        print(self.samples, self.lines, self.bands)
        envi.save_image(destanation + "\\" + name + ".hdr", self.img_array, 
                        dtype=self.img_array.dtype, interleave=self.interleave, ext=None, 
                        byteorder=self.byte_order, metadata=self.create_metadata())
        self.img_array = []


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
        
    def get_wavelength_str(self):
        final = '{'
        for x in range(0,len(self.wavelengths)):
            if x != 0:
                final = final + ','
            final = final + str(self.wavelengths[x])
        final = final + '}'
        return final
    
    def get_bandnames_str(self):
        final = '{'
        for x in range(0,len(self.wavelengths)):
            if x != 0:
                final = final + ','
            final = final + 'band' + str(x) + ': (' + str(self.wavelengths[x] + ')')
        final = final + '}'
        return final
            