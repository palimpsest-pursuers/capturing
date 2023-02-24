#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
from PIL import Image
import spectral.io.envi as envi


class CubeBuilder():
    img_array = []
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
    #band_names = '{band00: (356),band01: (385),band02: (395),band03: (420),band04: (450),band05: (470),band06: (490),band07: (520),band08: (560),band09: (590),band10: (615),band11: (630),band11: (660),band12: (730),band13: (850),band14: (940)}'
    
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

    def build(self):
        
        self.samples = self.img_array.shape[1]
        self.lines = self.img_array.shape[0]
        self.bands = self.img_array.shape[2]
        #self.img_array = np.transpose(self.img_array, (1,0,2))
        envi.save_image("C:\\Users\\cecel\\SeniorProject\\capturing\\test_datacube.hdr", self.img_array, 
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
            