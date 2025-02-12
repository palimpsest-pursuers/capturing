import sys
from controllers.camera_interface import CameraInterface
try:
    import PySpin
except ModuleNotFoundError:
    pass
import time
import numpy as np
from threading import Thread
import cv2


'''
Flir Blackfly Camera Controller 
Written by Sai Keshav Sasanapuri 
'''
class BlackflyController(CameraInterface):
    def __init__(self):
        """
        Constructor of the class. It calls initialize camera function. It also set exposure mode
        of the camera to manual and sets the exposure of the camera to default exposure. This function
        also disables auto-gain and auto exposure target grey. It finally un-initializes the camera.
        :param None
        :return: None
        """

        # initialize default exposure values
        self.ORIGINAL_EXPOSURE = 0.7
        self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16

        # initialize camera
        self.initialize_camera()

        try:
            if self.camera is not None:
                # Enable manual exposure
                if self.camera.ExposureAuto.GetAccessMode() != PySpin.RW:
                    raise PySpin.SpinnakerException("Initialization error")
                self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

                # Check if exposure mode is set to manual
                if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                    self.uninitialize_camera()
                    raise PySpin.SpinnakerException("Initialization error")

                # Set initial exposure in microseconds
                self.camera.ExposureTime.SetValue(self.get_microseconds(self.ORIGINAL_EXPOSURE))

                # Disable auto-gain
                self.camera.GainAuto.SetValue(PySpin.GainAuto_Off)

                # Disable auto exposure target grey
                self.camera.AutoExposureTargetGreyValueAuto.SetValue(PySpin.AutoExposureTargetGreyValueAuto_Off)

                # un-initialize camera
                self.uninitialize_camera()

        except PySpin.SpinnakerException as ex:
            raise ValueError("Initialization failed")

    def initialize_camera(self):
        """
        Initializes the camera for image acquisition.
        :return: None
        """
        try:
            # initializes camera variable to none
            self.camera = None

            # Get instances of all cameras for instance of system
            self.system = PySpin.System.GetInstance()
            cam_list = self.system.GetCameras()

            # fail initialization if no cameras were found
            if cam_list.GetSize() == 0:
                raise PySpin.SpinnakerException("Initialization error")

            # initialize camera variable using the first instance of the camera 
            self.camera = cam_list.GetByIndex(0)
            self.camera.Init()

            sNodemap = self.camera.GetTLStreamNodeMap()

            # Change bufferhandling mode to NewestOnly
            node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
            if not PySpin.IsReadable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
                return False

            # Retrieve entry node from enumeration node
            node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
            if not PySpin.IsReadable(node_newestonly):
                return False

            # Retrieve integer value from entry node
            node_newestonly_mode = node_newestonly.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

            #  Image acquisition must be ended when no more images are needed.
            self.camera.BeginAcquisition()

            cam_list.Clear()

        except PySpin.SpinnakerException as ex:
            raise ValueError("Initialization failed")

    def capture(self):
        """
        Captures an image from the camera.
        :return: Numpy array representing the captured image
        """
        try:
            # Check if camera is initialized
            if not self.camera.IsInitialized():
                return None

            # Get image from camera
            image_result = self.camera.GetNextImage()

            # Fault tolerance for incomplete images arrived from camera
            if image_result.IsIncomplete():
                max_tries = 5
                while image_result.IsIncomplete() and max_tries > 0:
                    image_result = self.camera.GetNextImage()

            # End capture process if it failed to get complete image from camera
            if image_result.IsIncomplete():
                return None

            # Convert image to numpy array
            img_numpy = image_result.GetNDArray()

            # Rotate image by 180 degrees
            img_numpy = np.rot90(img_numpy, 2)

            # Release the image
            image_result.Release()

            return img_numpy

        except PySpin.SpinnakerException as ex:
            return None
        except Exception as ex:
            return

    def capture_at_exposure(self, exposure, waveIndex):
        """
        Captures an image at a specific exposure.
        :param exposure: Exposure value to set before capturing
        :return: Numpy array representing the captured image
        """

        # change_exposure returns 0 if it failed to change camera exposure
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
            # Check if camera is initialized
            if not self.camera.IsInitialized():
                return 0

            # Get the new value to set for the camera exposure
            new_exposure = self.selected_exposure_array[waveIndex] * change

            # Checks if camera exposure can be changed manually
            if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                return 0

            # Set the new exposure for the camera
            self.camera.ExposureTime.SetValue(self.get_microseconds(new_exposure))

        except PySpin.SpinnakerException as ex:
            return 0
        return new_exposure

    def reset_exposure(self):
        """
        Resets the exposure of the camera to its original value.
        :return: None
        """
        # Reset the user selected exposure array to default exposures
        self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16

    def save_exposure(self, change, waveIndex):
        """
        Saves the exposure value after changing it by a specified factor.
        :param change: Factor by which to change the exposure
        :return: None
        """
        # Save the user selected exposure for a particular wavelength (advanced exposure mode)
        self.selected_exposure_array[waveIndex] = change * self.selected_exposure_array[waveIndex]

    def save_all_exposures(self, change):
        """
        saves camera exposure for all bands.
        :param change: Factor by which to change the exposure
        :return: None
        """
        # Save user selected exposures for all wavelengths (simple exposure mode)
        for i in range(len(self.selected_exposure_array)):
            self.selected_exposure_array[i] *= change

    def get_microseconds(self, seconds):
        """
        Converts seconds to microseconds.
        :param seconds: Time in seconds
        :return: Time in microseconds
        """
        # Blackfly camera sets exposure in microseconds
        return seconds * 1000000

    def uninitialize_camera(self):
        """
        Un-initialize the camera.
        :return: None
        """
        # Stop acquisition
        self.camera.EndAcquisition()

        # de-initialize camera
        self.camera.DeInit()

        # delete instance of camera
        del self.camera

        # clears memory allocated to buffer for camera
        self.system.ReleaseInstance()



