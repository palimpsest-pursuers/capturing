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
import debugpy 

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

    '''Adds raw object image ("img") to "img_array" and appends its wavelength to the list'''  
    def add_raw_image(self, img, wavelength):
        if (len(self.img_array) == 0):
            self.img_array = img
            if len(self.noise) > 0:
                self.final_array = np.subtract(img, self.noise)
            else:
                self.final_array = img
        else:
            self.img_array = np.dstack((self.img_array,img))
            if len(self.noise) > 0:
                sub = np.subtract(img, self.noise)
                self.final_array = np.dstack((self.final_array,sub))
            else:
                self.final_array = np.dstack((self.final_array,img))
        print(self.final_array.shape)
        self.wavelengths.append(wavelength)

    '''Adds raw flats image ("img") to "flats_array" '''
    def add_flat_image(self, img):
        print('flats',img.shape)
        if (len(self.flats_array) == 0):
            self.flats_array = img
        else:
            self.flats_array = np.dstack((self.flats_array,img))

    '''Subtracts flat image "img" from image in "final_array" at dimension "index" and updates "final_array" '''
    def subtract_flat(self, img, index):
        #nWhite = np.divide(np.subtract(img,np.min(img)), np.subtract(np.max(img),np.min(img)))
        filtered = ndimage.gaussian_filter(img, 20)
        copy = np.copy(self.img_array[:,:,index])
        divided = np.divide(copy,  filtered, where=(filtered!=0))

        #normalize this thing so we get stuff on a 0-1 scale
        divided = ((divided - np.min(divided)) / (np.max(divided) - np.min(divided))) 

        #convert the divided values into 255 uint8
        self.final_array[:,:,index] = (divided * 255).astype(np.uint8) 

    '''Sets noise image "noise" to "img"'''
    def add_noise_image(self, img):
        self.noise = img

    '''Rotates all image arrays 90 degrees "rotations" number of times'''
    def rotate90(self, rotations):
        self.img_array = np.rot90(self.img_array, rotations, (0,1))
        self.final_array = np.rot90(self.final_array, rotations, (0,1))
        if self.flats_array != []:
            self.flats_array = np.rot90(self.flats_array, rotations, (0,1))
        if self.noise != []:
            self.noise = np.rot90(self.noise, rotations, (0,1))

    '''Crops all image array to the given coordiantes'''
    def crop(self, x1, x2, y1, y2):
        self.img_array = self.img_array[x1:x2, y1:y2, : ]
        self.final_array = self.final_array[x1:x2, y1:y2, : ]
        if self.flats_array != []:
            self.flats_array = self.flats_array[x1:x2, y1:y2, : ]
        
    '''Generates a binary image where all values in the provided coordiates are 1 and everything else is 0'''    
    def generateBinaryImage(self, x1, x2, y1, y2):
        zeros = np.zeros(self.final_array.shape)
        zeros[x1:x2, y1:y2, :] = 1.0
        return zeros

    '''Calibrate the final image using "binaryImage"'''
    def calibrate(self, binaryImage, progress):
        """
        temps = self.final_array.astype(float) * binaryImage
        cnt2 = np.sum(binaryImage[binaryImage != 0])
        mean_temps = [np.mean(temps[:,:,i][binaryImage != 0]) for i in range(self.final_array.shape[2])]
        dataCube = self.final_array.astype(float) / np.array(mean_temps)[None, None, :]
        dataCube[dataCube > 1] = 1
        self.final_cube = dataCube
        """

        
        #%temps = double(dataCube).*double(binaryImage_cube);
        #I just picked float32 because I know that's what processing likes for cubes
        temps = self.final_array.astype(np.float32) * binaryImage
        progress.setValue(2)

        #count all the pixels in binary image where binary image is not 0
        #I don't think we need to sum twice because that where clause should
        #just count the 1s (we could use binaryImage == 1). 
        #If not, use the sum based on axis like I have below for meantemp
        #%cnt2 = sum(sum(binaryImage(binaryImage ~= 0)));
        ones_sum = np.sum(binaryImage, axis = (0,1), where=(binaryImage != 0))
        progress.setValue(3)
        #one_sum_per_band = np.sum(ones_sum_col, axis = 1)

        #sum up all the pixel values under the mask for each array, divide by total number of ones
        #to get the mean pixel value under the mask for each band                        
        #%meantemp = sum(sum(temps))/cnt2;
        #sum_columns = np.sum(temps, axis=0)
        #sum_rows = np.sum(sum_columns, axis=1)
        #meantemp = sum_rows / one_sum_per_band
        meantemp = np.sum(temps, axis=(0,1)) / ones_sum
        progress.setValue(4)

        #take that mean value for each band and repeat it to make it the 
        #size of the original image                        
        #%meantemp_cube = repmat(meantemp,[size(dataCube,1) size(dataCube,2),1]);
        #meantemp_cube = np.repeat(meantemp, (self.final_array.shape[0], self.final_array.shape[1], 1))
        meantemp_cube = np.broadcast_to(meantemp,self.final_array.shape)
        progress.setValue(5)
                        
        #%calibrate data - divide by mean spectralon per band  
        #Combining these two because it doesn't look too bad                   
        #%dataCube = double(dataCube)./meantemp_cube;
        #%dataCube(dataCube > 1) = 1;  

        self.final_array = np.clip((self.final_array / meantemp_cube), a_max=1, a_min=0)
        progress.setValue(6)
        


    def auto_calibrate(self, img):
        pass
    
    '''incomplete'''
    def stretch_image(self, percent):
        out = np.empty_like(self.img_array)

        for i in range(0,self.img_array.shape[2]):
            band = self.img_array[:,:,i]
            tempSorted = band.sort(1)
        return out
    
    '''Revert flat subraction and calibration'''
    def revert_final(self):
        self.final_array = self.img_array.copy()
        if len(self.noise) != 0:
            for x in range(0,len(self.wavelengths)):
                img = self.final_array[:,:,x].copy()
                self.final_array[:,:,x] = np.subtract(img, self.noise)
        print("image",self.img_array.shape)
        print("final",self.final_array.shape)

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
        except:
            return ("Image cube with this name already exists in this folder.\n"
                    + "Please delete cube with the same name or choose a diffrent folder.\n")
        
        # save all raw object images as individual tiffs in its own subdirectory
        w = 0
        for x in range(0, len(self.wavelengths)):
            img = np.copy(self.img_array)[:,:,w]
            imwrite(rawPath + "\\" + name + "-"+self.wavelengths[w]+".tif", img,shape=(img.shape))
            w = w + 1

        if len(self.flats_array) > 0 and self.img_array.shape == self.flats_array.shape:
            # save all raw flats images as individual tiffs in its own subdirectory
            flatsPath = os.path.join(destanation, "Flat Images")
            os.makedirs(flatsPath)

            w = 0
            for x in range(0, len(self.wavelengths)):
                flat = np.copy(self.flats_array)[:,:,w]
                imwrite(flatsPath + "\\" + name + "-"+self.wavelengths[w]+".tif", flat,shape=(img.shape))
                w = w + 1

        if len(self.noise) > 0:
            # save noise image
            imwrite(destanation + "\\" + name + "-noise.tif", self.noise,shape=(self.noise.shape))
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
        for x in range(0,len(self.wavelengths)):
            if x != 0:
                final = final + ','
            final = final + str(self.wavelengths[x])
        final = final + '}'
        return final
    
    '''Get bandnames as a string'''
    def get_bandnames_str(self):
        final = '{'
        for x in range(0,len(self.wavelengths)):
            if x != 0:
                final = final + ','
            final = final + 'band' + str(x) + ': (' + str(self.wavelengths[x] + ')')
        final = final + '}'
        return final
            