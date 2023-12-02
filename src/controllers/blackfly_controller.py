import sys

from controllers.camera_interface import CameraInterface
import PySpin
import numpy as np
import cv2


class BlackflyController(CameraInterface):
    def __init__(self):
        self.exposure = 0.7
        self.ORIGINAL_EXPOSURE = 0.7
        self.initialize_camera()

        try:
            self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')
            # Set initial exposure (you can modify this value)
            # Set the initial exposure time in microseconds
            if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                self.uninitialize_camera()
                return

            self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            self.camera.ExposureTime.SetValue(self.get_microseconds(self.exposure))
            print("Exposure changed to: ", self.ORIGINAL_EXPOSURE)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return
        self.uninitialize_camera()

    def interrupt_handler(signal, frame):
        print("\nprogram exiting gracefully")
        sys.exit(0)

    def initialize_camera(self):
        try:
            self.camera = None
            self.system = PySpin.System.GetInstance()
            cam_list = self.system.GetCameras()
            if cam_list.GetSize() == 0:
                print("No cameras found.")
                return

            self.camera = cam_list.GetByIndex(0)
            self.camera.Init()

            #  Image acquisition must be ended when no more images are needed.
            self.camera.BeginAcquisition()

            print('Blackfly Acquiring images...')

            cam_list.Clear()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

    def capture(self):
        try:
            if not self.camera.IsInitialized():
                print("Camera not initialized.")
                return None

            image_result = self.camera.GetNextImage()

            if image_result.IsIncomplete():
                print("Image incomplete.")
                return None

            width = image_result.GetWidth()
            height = image_result.GetHeight()

            # Convert image to numpy array
            img_numpy = image_result.GetNDArray()
            L = img_numpy
            u = np.mean(L)
            LP = cv2.Laplacian(L, cv2.CV_64F).var()
            self.sharpness = 1 / np.sum(LP / u) * 1000

            # Release the image
            image_result.Release()
            print("Blackfly image captured and sent")
            return img_numpy

        except PySpin.SpinnakerException as ex:
            print("Error:", ex)
            return None

    def capture_at_exposure(self, exposure):
        if self.change_exposure(exposure) == 0:
            return
        return self.capture()

    def change_exposure(self, change):
        try:
            if not self.camera.IsInitialized():
                print("Camera not initialized.")
                return 0

            new_exposure = self.exposure * change
            if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return 0

            self.camera.ExposureTime.SetValue(self.get_microseconds(new_exposure))
            print("Exposure changed to: ", new_exposure)
            print("when told to change by:", change)

        except PySpin.SpinnakerException as ex:
            print("Error:", ex)
            return 0
        return new_exposure

    def reset_exposure(self):
        try:
            self.exposure = self.ORIGINAL_EXPOSURE
            self.initialize_camera()
            if not self.camera.IsInitialized():
                print("Camera not initialized.")
                return

            if self.camera.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return 0

            self.camera.ExposureTime.SetValue(self.get_microseconds(self.ORIGINAL_EXPOSURE))
            print("Exposure changed to: ", self.ORIGINAL_EXPOSURE)

        except PySpin.SpinnakerException as ex:
            print("Error:", ex)
        self.uninitialize_camera()

    def save_exposure(self, change):
        self.initialize_camera()
        self.exposure = self.change_exposure(change)
        print("Saving exposure at " + str(self.exposure))
        self.uninitialize_camera()

    def get_microseconds(self, seconds):
        return seconds * 1000000

    def uninitialize_camera(self):
        self.camera.EndAcquisition()
        self.camera.DeInit()
        del self.camera
        self.system.ReleaseInstance()

