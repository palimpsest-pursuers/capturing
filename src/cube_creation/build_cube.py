#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
from PIL import Image
import spectral.io.envi as envi


class CubeBuilder():
    destination_dir = ""
    filenames = None
    wavelengths = '{356,385,395,420,450,470,490,520,560,590,615,630,660,730,850,940}'
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
    band_names = '{band00: (356),band01: (385),band02: (395),band03: (420),band04: (450),band05: (470),band06: (490),band07: (520),band08: (560),band09: (590),band10: (615),band11: (630),band11: (660),band12: (730),band13: (850),band14: (940)}'
    
    def __init__(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        #dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("Images (*.tiff)")
        
        self.filenames = dlg.getOpenFileNames(None,"Select captured images",'',"Images (*.tiff)",)[0]
        self.build()
        

        

    def build(self):
        img = Image.open(self.filenames[0])
        #A = set(self.filenames[0].split())
        array = np.array(img)
        for x in range(1, len(self.filenames)):
            img = Image.open(self.filenames[x])
            array2 = np.array(img)
            array = np.dstack((array,array2))
            print(self.filenames[x],"added")
            #B = set(self.filenames[x].split())
            #self.wavelengths.append(str(A.symmetric_difference(B)))
        self.samples = array.shape[1]
        self.lines = array.shape[0]
        self.bands = array.shape[2]
        array = np.transpose(array, (1,0,2))
        envi.save_image("C:\\Users\\cecel\\SeniorProject\\capturing\\test_datacube.hdr", array, 
                        dtype=array.dtype, interleave=self.interleave, ext=None, 
                        byteorder=self.byte_order, metadata=self.create_metadata())


    def create_metadata(self):
        return {"wavelengths": self.wavelengths,
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
                    "band names": self.band_names}
        
        
        
    def create_hdr(self):
        pass
            