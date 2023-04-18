#from PyQt5 import QtCore, QtGui, QtWidgets
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
from PIL import Image
import spectral.io.envi as envi
import scipy.ndimage as ndimage
from tifffile import imwrite


class CubeBuilder():
    img_array = []
    flats_array = []
    final_array = []
    noise = []
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
        if len(self.noise) > 0:
            img = np.subtract(img, self.noise)
        #print(img.shape)
        if (self.img_array == []):
            self.img_array = img
        else:
            self.img_array = np.dstack((self.img_array,img))
        #print(self.img_array.shape)
        self.wavelengths.append(wavelength)

    def add_flat_image(self, img):
        print('flats',img.shape)
        if (self.flats_array == []):
            self.flats_array = img
        else:
            self.flats_array = np.dstack((self.flats_array,img))

    def subtract_flat(self, img, index):
        filtered = ndimage.gaussian_filter(img, 20)
        copy = np.copy(self.img_array[:,:,index])
        divided = copy / filtered
        self.final_array[:,:,index] = divided

    def add_noise_image(self, img):
        self.noise = img


    def rotate90(self, rotations):
        self.img_array = np.rot90(self.img_array, rotations, (0,1))

    def crop(self, x1, x2, y1, y2):
        self.img_array = self.img_array[x1:x2, y1:y2, : ]
        self.final_array = self.final_array[x1:x2, y1:y2, : ]
        if len(self.flats_array) > 0:
            self.flats_array = self.flats_array[x1:x2, y1:y2, : ]
        
    def generateBinaryImage(self, x1, x2, y1, y2):
        #flatShape = ([0], self.final_array.shape[1])
        zeros = np.zeros(self.final_array.shape)
        zeros[x1:x2, y1:y2, :] = 1.0
        return zeros

    def calibrate(self, binaryImage):
        temps = self.final_array.astype(float) * binaryImage
        cnt2 = np.sum(binaryImage[binaryImage != 0])
        mean_temps = [np.mean(temps[:,:,i][binaryImage != 0]) for i in range(self.final_array.shape[2])]
        dataCube = self.final_array.astype(float) / np.array(mean_temps)[None, None, :]
        dataCube[dataCube > 1] = 1
        self.final_cube = dataCube

        """
        //%temps = double(dataCube).*double(binaryImage_cube);
        //I just picked float32 because I know that's what processing likes for cubes
        temps = self.final_array.astype(np.float32) * binaryImage


        //count all the pixels in binary image where binary image is not 0
        //I don't think we need to sum twice because that where clause should
        //just count the 1s (we could use binaryImage == 1). 
        //If not, use the sum based on axis like I have below for meantemp
        //%cnt2 = sum(sum(binaryImage(binaryImage ~= 0)));
        ones_count = np.sum(binaryImage, where=(binaryImage != 0))

        //sum up all the pixel values under the mask for each array, divide by total number of ones
        //to get the mean pixel value under the mask for each band                        
        //%meantemp = sum(sum(temps))/cnt2;
        sum_columns = np.sum(temps, axis=0)
        sum_rows = np.sum(temps, axis=1)
        meantemp = sum_rows / ones_count

        //take that mean value for each band and repeat it to make it the 
        //size of the original image                        
        //%meantemp_cube = repmat(meantemp,[size(dataCube,1) size(dataCube,2),1]);
        meantemp_cube = np.repeat(meantemp, (self.final_array.shape[0], self.final_array.shape[1], 1)

                        
        //%calibrate data - divide by mean spectralon per band  
        //Combining these two because it doesn't look too bad                   
        //%dataCube = double(dataCube)./meantemp_cube;
        //%dataCube(dataCube > 1) = 1;  

        self.final_cube = np.clip((self.final_array / meantemp_cube), a_max=1)
        """


    def auto_calibrate(self, img):
        pass

    def stretch_image(self, percent):
        out = np.empty_like(self.img_array)

        for i in range(0,self.img_array.shape[2]):
            band = self.img_array[:,:,i]
            tempSorted = band.sort(1)
        return out
    
    def revert_final(self):
        self.final_array = self.img_array.copy()
        print("image",self.img_array.shape)
        print("final",self.final_array.shape)

    def build(self, destanation, name):
        self.samples = self.final_array.shape[1]
        self.lines = self.final_array.shape[0]
        self.bands = self.final_array.shape[2]

        print(self.samples, self.lines, self.bands)
        envi.save_image(destanation + "\\" + name + ".hdr", self.final_array, 
                        dtype=self.final_array.dtype, interleave=self.interleave, ext=None, 
                        byteorder=self.byte_order, metadata=self.create_metadata())
        # self.img_array = []

        rawPath = os.path.join(destanation, "Raw Images")
        os.makedirs(rawPath)

        w = 0
        for x in range(0, len(self.wavelengths)):
            img = np.copy(self.img_array)[:,:,w]
            imwrite(rawPath + "\\" + name + "-"+self.wavelengths[w]+".tif", img)
            w = w + 1

        if len(self.flats_array) > 0 and self.img_array.shape == self.flats_array.shape:
            flatsPath = os.path.join(destanation, "Flat Images")
            os.makedirs(flatsPath)

            w = 0
            for x in range(0, len(self.wavelengths)):
                flat = np.copy(self.flats_array)[:,:,w]
                imwrite(flatsPath + "\\" + name + "-"+self.wavelengths[w]+".tif", flat)
                w = w + 1


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
            