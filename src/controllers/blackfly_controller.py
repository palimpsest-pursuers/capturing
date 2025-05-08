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
        self.acquisition_mode = None
        self.camera = None
        self.system = None
        self.cam_list = None


        # initialize camera
        ret = self.initialize_camera()
        if ret["Success"]:
            try:
                if self.camera is not None:
                    # Enable manual exposure
                    self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

                    # Set initial exposure in microseconds
                    self.camera.ExposureTime.SetValue(self.get_microseconds(self.ORIGINAL_EXPOSURE))

                    # Disable auto-gain
                    self.camera.GainAuto.SetValue(PySpin.GainAuto_Off)

                    # Disable auto exposure target grey
                    self.camera.AutoExposureTargetGreyValueAuto.SetValue(PySpin.AutoExposureTargetGreyValueAuto_Off)

                    # Set Acquisition mode to single frame
                    self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
                    self.acquisition_mode = "SingleFrame"

                    sNodemap = self.camera.GetTLStreamNodeMap()

                    # Change bufferhandling mode to NewestOnly
                    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))

                    # Retrieve entry node from enumeration node
                    node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')

                    # Retrieve integer value from entry node
                    node_newestonly_mode = node_newestonly.GetValue()

                    # Set integer value from entry node as new value of enumeration node
                    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

                    # self.uninitialize_camera()

            except PySpin.SpinnakerException as ex:
                raise ValueError("Initialization failed")
        else:
            raise ValueError("Initialization failed")

    def initialize_camera(self, mode="SingleFrame"):
        """
        Initializes the camera for image acquisition.
        :return: None
        """
        try:
            if self.check_camera_initialized():
                return {"Success": True, "Error": None}
                
            # initializes camera variable to none
            self.camera = None

            # Get instances of all cameras for instance of system
            self.system = PySpin.System.GetInstance()
            self.cam_list = self.system.GetCameras()

            # fail initialization if no cameras were found
            if self.cam_list.GetSize() == 0:
                raise PySpin.SpinnakerException("Initialization error")

            # initialize camera variable using the first instance of the camera 
            self.camera = self.cam_list.GetByIndex(0)
            self.camera.Init()
            return {"Success": True, "Error": None}

        except PySpin.SpinnakerException as ex:
            self.uninitialize_camera()
            return {"Success": False, "Error": ex}
        
    def check_camera_initialized(self) -> bool:
        if self.camera is None:
            self.uninitialize_camera()
            return False
        elif not self.camera.IsInitialized():
            self.uninitialize_camera()
            return False
        try:
            # Try reading a property from the camera
            self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        except Exception as ex:
            # If reading fails, camera is not connected physically
            self.uninitialize_camera()
            return False
        return True
        
    def change_acquisition_mode(self, mode: str):
        # Stop acquisition if ongoing
        if self.camera.IsStreaming():
            self.camera.EndAcquisition()
        self.acquisition_mode = mode
        if self.acquisition_mode == 'SingleFrame':
            self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        elif self.acquisition_mode == 'Continuous':
            self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

    def capture(self):
        """
        Captures an image from the camera.
        :return: Numpy array representing the captured image
        """
        try:
            # Check if camera is initialized
            if not self.camera.IsInitialized():
                return {"Success": False, "Image": None}

            # if self.acquisition_mode == 'SingleFrame':
            #     self.camera.BeginAcquisition()

            # Get image from camera
            image_result = self.camera.GetNextImage()

            # Fault tolerance for incomplete images arrived from camera
            if image_result.IsIncomplete():
                max_tries = 5
                while image_result.IsIncomplete() and max_tries > 0:
                    image_result = self.camera.GetNextImage()

            # End capture process if it failed to get complete image from camera
            if image_result.IsIncomplete():
                return {"Success": False, "Image": None}

            # Convert image to numpy array
            img_numpy = image_result.GetNDArray()

            # Rotate image by 180 degrees
            img_numpy = np.rot90(img_numpy, 2)

            # Release the image
            image_result.Release()

            # if self.acquisition_mode == 'SingleFrame':
            #     self.camera.EndAcquisition()

            return {"Success": True, "Image": img_numpy}

        except PySpin.SpinnakerException as ex:
            return {"Success": False, "Image": None}
        except Exception as ex:
            return {"Success": False, "Image": None}

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
        if self.camera is not None and self.camera.IsStreaming():
            self.camera.EndAcquisition()

        # de-initialize camera
        if self.camera is not None:
            self.camera.DeInit()
            # delete instance of camera
            del self.camera
            self.camera = None

        if self.cam_list is not None:
            self.cam_list.Clear()
            self.cam_list = None
        try:
            if self.system is not None:
                # clears memory allocated to buffer for camera
                self.system.ReleaseInstance()
                self.system = None
        except PySpin.SpinnakerException as ex:
            pass


