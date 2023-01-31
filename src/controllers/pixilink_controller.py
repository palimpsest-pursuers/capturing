from controllers.camera_interface import CameraInterface
from pixelinkWrapper import*
from ctypes import*
import time
import numpy as np
import sys, signal

import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from matplotlib import pyplot as plt

class PixilinkController(CameraInterface):
    hCamera = None
    frame = None


    def __init__(self):
        self.initialize_camera()
        
        '''if not(PxLApi.apiSuccess(ret1[0])):
            print("Error: Unable to initialize a camera! rc = %i" % ret[0])
            return 1
        #self.hCamera = ret1'''
        ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE)
        if not(PxLApi.apiSuccess(ret[0])):
            print("!! Attempt to get exposure returned %i!" % ret[0])
            self.uninitialize_camera()
            return
        
        params = ret[2]
        exposure = params[0]
        self.ORIGINAL_EXPOSURE = exposure
        self.exposure = exposure
        self.uninitialize_camera()
        
    #interrupt handler
    def interrupt_handler(signal, frame):
        print("\nprogram exiting gracefully")
        sys.exit(0)

        # Just to define our image buffer;  One that's large enough for the Pixelink camera being used
    MAX_WIDTH = 5000   # in pixels
    MAX_HEIGHT = 5000  # in pixels
    MAX_BYTES_PER_PIXEL = 3

    def initialize_camera(self):
        ret = PxLApi.initialize(0)
        if not(PxLApi.apiSuccess(ret[0])):
            print("Error: Unable to initialize a camera! rc = %i" % ret[0])
            return 1

        #self.exposure = 1
        self.hCamera = ret[1]

        # get proper camera size, create frame from that
        ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.ROI)
        params = ret[2]
        roiWidth = params[PxLApi.RoiParams.WIDTH]
        roiHeight = params[PxLApi.RoiParams.HEIGHT]

        self.frame = np.zeros([int(roiHeight),int(roiWidth)], dtype=np.uint8)

        # Start the stream
        ret = PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.START)

    def capture(self):
        ret = self.get_next_frame(5)
        print(ret)
        #frame was successful
        if PxLApi.apiSuccess(ret[0]):
            #calculate sharpness
            '''img_HLS = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HLS)
            L = img_HLS[:, :, 1]
            u = np.mean(L)
            LP = cv2.Laplacian(L, cv2.CV_64F).var()
            self.sharpness = 1/np.sum(LP/u)*1000'''
            self.sharpness = 9000
            print("success")
            #update frame
            return self.frame

        #frame was unsuccessful
        else:
            print("Too many errors encountered, exiting")
            sys.exit(-1)   

        

    """
    A robust wrapper around PxLApi.getNextFrame.
    This will handle the occasional error that can be returned by the API because of timeouts. 
    Note that this should only be called when grabbing images from a camera NOT currently configured for triggering. 
    """
    def get_next_frame(self, maxNumberOfTries):

        ret = (PxLApi.ReturnCode.ApiUnknownError,)

        for i in range(maxNumberOfTries):
            ret = PxLApi.getNextNumPyFrame(self.hCamera, self.frame)
            if PxLApi.apiSuccess(ret[0]):
                print("worked")
                return ret
            else:
                # If the streaming is turned off, or worse yet -- is gone?
                # If so, no sense in continuing.
                if PxLApi.ReturnCode.ApiStreamStopped == ret[0] or \
                    PxLApi.ReturnCode.ApiNoCameraAvailableError == ret[0]:
                    print("no stream")
                    return ret
                else:
                    print("getNextFrame returned %i" % ret[0])

        # Ran out of tries, so return whatever the last error was.
        print("tried I guess")
        return ret

    def capture_at_exposure(self, exposure):
        if self.change_exposure(exposure) == 0:
            return
        return self.capture()

    def change_exposure(self, change):
        #self.initialize_camera()
        ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE)
        #print(ret)
        #print(ret[2][0])
        if not(PxLApi.apiSuccess(ret[0])):
            print("!! Attempt to get exposure returned %i!" % ret[0])
            #self.uninitialize_camera()
            return 0
        
        params = ret[2]
        exposure = params[0]
        exposure =  self.exposure * change

        print("Changed to: ")
        print(exposure)
        print("when told to change by:")
        print(change)

        params[0] = exposure

        ret = PxLApi.setFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE, PxLApi.FeatureFlags.MANUAL, params)
        if (not PxLApi.apiSuccess(ret[0])):
            print("!! Attempt to set exposure returned %i!" % ret[0])
            return 0
        #self.exposure = exposure
        #self.uninitialize_camera()
        return exposure
    
    def reset_exposure(self):
        self.exposure = self.ORIGINAL_EXPOSURE
        self.initialize_camera()
        ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE)
        #print(ret)
        #print(ret[2][0])
        if not(PxLApi.apiSuccess(ret[0])):
            print("!! Attempt to get exposure returned %i!" % ret[0])
            self.uninitialize_camera()
            return

        params = ret[2]
        params[0] = self.ORIGINAL_EXPOSURE

        ret = PxLApi.setFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE, PxLApi.FeatureFlags.MANUAL, params)
        if (not PxLApi.apiSuccess(ret[0])):
            print("!! Attempt to set exposure returned %i!" % ret[0])
        self.uninitialize_camera()

    def save_exposure(self, change):
        self.initialize_camera()
        self.exposure = self.change_exposure(change)
        print("Saving exposure at " + str(self.exposure))
        self.uninitialize_camera()

    def uninitialize_camera(self):
        #turn off stream state 
        ret = PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.STOP)
        assert PxLApi.apiSuccess(ret[0]), "setStreamState with StreamState.STOP failed"

        ret = PxLApi.uninitialize(self.hCamera)
        assert PxLApi.apiSuccess(ret[0]), "uninitialize failed"