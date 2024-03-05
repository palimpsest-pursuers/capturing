import sys

from controllers.camera_interface import CameraInterface
import PySpin
import numpy as np
from scipy.ndimage import gaussian_gradient_magnitude
import cv2

'''
Flir Blackfly Camera Controller 
Written by Sai Keshav Sasanapuri 
'''
class BlackflyController(CameraInterface):
    def __init__(self):
        """
        Constructor of the class. It calls initialize camera function. It also set exposure mode
        of the camera to manual and sets the exposure of the camera to default exposure
        :param None
        :return: None
        """
        self.ORIGINAL_EXPOSURE = 0.7
        self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16
        self.camera = None
        self.initialize_camera()

        try:
            if self.camera is not None:
                """Enable manual exposure"""
                if self.camera.ExposureAuto.GetAccessMode() != PySpin.RW:
                    print('Unable to disable automatic exposure. Aborting...')
                    return
                self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
                print('Automatic exposure disabled...')
                # Check if exposure mode is set to manual
                if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                    print('Unable to set exposure time. Aborting...')
                    self.uninitialize_camera()
                    return
                # Set initial exposure (you can modify this value)
                # Set the initial exposure time in microseconds
                self.camera.ExposureTime.SetValue(self.get_microseconds(self.ORIGINAL_EXPOSURE))
                print("Exposure changed to: ", self.ORIGINAL_EXPOSURE)
                self.camera.GainAuto.SetValue(PySpin.GainAuto_Off)
                print("Automatic gain disabled")
                self.camera.AutoExposureTargetGreyValueAuto.SetValue(PySpin.AutoExposureTargetGreyValueAuto_Off)
                print("Automatic exposure target grey disabled")
                self.uninitialize_camera()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            raise ValueError("Initialization failed")

    def interrupt_handler(signal, frame):
        print("\nprogram exiting gracefully")
        sys.exit(0)

    def initialize_camera(self):
        """
        Initializes the camera for image acquisition.
        :return: None
        """
        try:
            self.camera = None
            self.system = PySpin.System.GetInstance()
            cam_list = self.system.GetCameras()
            if cam_list.GetSize() == 0:
                print("No cameras found.")
                # return
                raise ValueError("No cameras found during initialization")

            self.camera = cam_list.GetByIndex(0)
            self.camera.Init()

            sNodemap = self.camera.GetTLStreamNodeMap()

            # Change bufferhandling mode to NewestOnly
            node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
            if not PySpin.IsReadable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
                print('Unable to set stream buffer handling mode.. Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
            if not PySpin.IsReadable(node_newestonly):
                print('Unable to set stream buffer handling mode.. Aborting...')
                return False

            # Retrieve integer value from entry node
            node_newestonly_mode = node_newestonly.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

            #  Image acquisition must be ended when no more images are needed.
            self.camera.BeginAcquisition()
            print('Flir Initialized')

            cam_list.Clear()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            raise ValueError("Initialization failed")

    def capture(self):
        """
        Captures an image from the camera.
        :return: Numpy array representing the captured image
        """
        try:
            if not self.camera.IsInitialized():
                print("Camera not initialized.")
                return None

            image_result = self.camera.GetNextImage()

            if image_result.IsIncomplete():
                print("Image incomplete.")
                max_tries = 5
                while image_result.IsIncomplete() and max_tries > 0:
                    image_result = self.camera.GetNextImage()
                    print("Image incomplete.")
                print("Incomplete Image received even after multiple tries")
                return None

            # Convert image to numpy array
            img_numpy = image_result.GetNDArray()
            # Rotate image by 180 degrees
            img_numpy = np.rot90(img_numpy, 2)
            # Calculate Sharpness
            img_normalized = (img_numpy - np.min(img_numpy)) / (np.max(img_numpy) - np.min(img_numpy))
            # Calculate gradient
            fx, fy = np.gradient(img_normalized * 255)
            # Find maximum gradient
            self.sharpness = np.max([np.max(fx), np.max(fy)])
            print("sharpness: ", self.sharpness)

            # Release the image
            image_result.Release()
            return img_numpy

        except PySpin.SpinnakerException as ex:
            print("Error:", ex)
            return None

    def capture_at_exposure(self, exposure, waveIndex):
        """
        Captures an image at a specific exposure.
        :param exposure: Exposure value to set before capturing
        :return: Numpy array representing the captured image
        """
        if self.change_exposure(exposure, waveIndex) == 0:
            return
        return self.capture()

    def change_exposure(self, change, waveIndex):
        """
        Changes the exposure of the camera by a specified factor.
        :param change: Factor by which to change the exposure
        :return: New exposure value
        """
        try:
            if not self.camera.IsInitialized():
                print("Camera not initialized.")
                return 0

            new_exposure = self.selected_exposure_array[waveIndex] * change
            if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return 0

            self.camera.ExposureTime.SetValue(self.get_microseconds(new_exposure))
            print("Exposure changed to: ", new_exposure, " when told to change by:", change)

        except PySpin.SpinnakerException as ex:
            print("Error:", ex)
            return 0
        return new_exposure

    def reset_exposure(self):
        """
        Resets the exposure of the camera to its original value.
        :return: None
        """
        self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16

    def save_exposure(self, change, waveIndex):
        """
        Saves the exposure value after changing it by a specified factor.
        :param change: Factor by which to change the exposure
        :return: None
        """
        self.selected_exposure_array[waveIndex] = change * self.selected_exposure_array[waveIndex]
        print("Saving exposure for led " + str(waveIndex) + " at " + str(self.selected_exposure_array[waveIndex]))

    def save_all_exposures(self, change):
        """
        saves camera exposure for all bands.
        :param change: Factor by which to change the exposure
        :return: None
        """
        for i in range(len(self.selected_exposure_array)):
            self.selected_exposure_array[i] *= change
        print("Saving exposure for all bands at: ", self.selected_exposure_array)

    def get_microseconds(self, seconds):
        """
        Converts seconds to microseconds.
        :param seconds: Time in seconds
        :return: Time in microseconds
        """
        return seconds * 1000000

    def uninitialize_camera(self):
        """
        Un-initialize the camera.
        :return: None
        """
        self.camera.EndAcquisition()
        self.camera.DeInit()
        del self.camera
        self.system.ReleaseInstance()
        print("camera un-initialized")

    # def __del__(self):
    #     """
    #     Destructor to clean up resources when the object is destroyed.
    #     :return: None
    #     """
    #     try:
    #         if self.camera is not None:
    #             self.camera.EndAcquisition()
    #             self.camera.DeInit()
    #         del self.camera
    #         self.system.ReleaseInstance()
    #     except PySpin.SpinnakerException as ex:
    #         print('Error: %s' % ex)
    #         return


