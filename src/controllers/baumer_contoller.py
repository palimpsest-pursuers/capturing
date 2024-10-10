"""
Baumer Camera controller 
Writen by Julia Schenatto (IFUSP)
"""

import sys
use_numpy = False
try:
    import numpy as np
    use_numpy = True
except ImportError:
    pass
from camera_interface import CameraInterface
try:
    import neoapi  # python library from Baumer
except Exception as ex:
    print("Error importing neoapi:", ex)
    sys.exit(1)


class BaumerController(CameraInterface):
    def __init__(self):
        """
        Constructor of the class. It calls initialize camera function. It also set exposure mode
        of the camera to manual and sets the exposure of the camera to default exposure
        :param None
        :return: None
        """
        self.ORIGINAL_EXPOSURE = 0.7  # seconds
        self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16
        self.camera = None
        self.initialize_camera()  # Initializes the camera settings

        try:
            if not self.camera.f.AutoExposure.IsWritable():
                print("Auto exposure cannot be modified.")
            self.camera.f.AutoExposure.Set(False)  # Disable AutoExposure
            print("Auto exposure disabled.")

            # Configure exposure time
            self.camera.f.ExposureTime.Set(self.get_microseconds(self.ORIGINAL_EXPOSURE))
            print("Exposure set to:", self.ORIGINAL_EXPOSURE)

            # Disable automatic gain
            if self.camera.f.GainAuto.IsWritable():
                self.camera.f.GainAuto.Set(False)
                print("Automatic gain disabled.")

            # Disable automatic gray scale
            if self.camera.f.AutoGrayScale.IsWritable():
                self.camera.f.AutoGrayScale.Set(False)
                print("Automatic gray scale disabled.")
            self.uninitialize_camera()
        
        except (neoapi.NeoException, Exception) as exc:
            print('Error:', exc)
            raise ValueError("Camera initialization failed")

    def interrupt_handler(signal, frame): 
        print("\nprogram exiting gracefully")
        sys.exit(0)

    def initialize_camera(self):
        """
        Initialize the camera for the acquisition.
        :return: None
        """
        try:
            self.camera = None
            self.camera = neoapi.Cam()
            self.camera.Connect()

            if not self.camera.IsStreaming():
                print("Camera not initialized.")
                raise ValueError("No cameras found during initialization")
            
            ################################################### Might be able to remove this for performance
            # Initialize buffer for image capture
            payloadsize = self.camera.f.PayloadSize.Get()
            buf = MyBuffer(payloadsize) # defined at the end of the code
            buf.myContent = 1  # Only store one image
            self.camera.AddUserBuffer(buf)
            self.camera.SetUserBufferMode(True)

            self.camera.AcquisitionStart()
            print('Baumer camera initialized.')
            # no list necessary, by the looks of the python wrapper from Baumer.
            ####################################################

        except (neoapi.NeoException, Exception) as exc:
            print('Initialization error:', exc)
            raise ValueError("Baumer Blackfly initialization failed")

    def capture(self):
        """Capture an image from the camera."""
        try:
            if not self.camera.IsStreaming():
                print("Camera not initialized.")
                return None

            #self.camera.AcquisitionStart()  # Start acquisition
            image_result = self.camera.GetImage()  # Get the next image if camera is streaming

            if image_result.IsEmpty():
                print("Incomplete image.")
                max_tries = 5
                while image_result.IsEmpty() and max_tries > 0:
                    image_result = self.camera.GetImage()
                    print("Image is incomplete.")
                    max_tries -= 1
                if image_result.IsEmpty():
                    print("Incomplete image received even after multiple tries.")
                    return None
            
            # Convert image to numpy array
            image_numpy = image_result.GetNPArray()
            image_numpy = np.rot90(image_numpy, 2)  # Rotate image 180 degrees
            # Normalize the image
            image_normalized = (image_numpy - np.min(image_numpy)) / (np.max(image_numpy) - np.min(image_numpy))
            # Calculate gradient
            fx, fy = np.gradient(image_normalized * 255)
            # Find maximum sharpness
            self.sharpness = np.max([np.max(fx), np.max(fy)])
            print("Sharpness:", self.sharpness)

            # Clear image buffer <--> stands for the .Release() from FLIR wrapper
            self.camera.ClearImages()
            return image_numpy

        except (neoapi.NeoException, Exception) as exc:
            print('Error:', exc)
            return None

    def capture_at_exposure(self, exposure, waveIndex):
        """
        Captures an image at a specific exposure.
        :param exposure: Exposure value to set before capturing
        :return: Numpy array representing the captured image
        """
        if self.change_exposure(exposure, waveIndex) == 0: # definido abaixo
            return
        return self.capture()

    def change_exposure(self, change, waveIndex):
        """
        Changes the exposure of the camera by a specified factor.
        :param change: Factor by which to change the exposure
        :return: New exposure value
        """
        try:
            if not self.camera.IsStreaming():
                print("Camera not initialized.")
                return 0
            new_exposure = self.selected_exposure_array[waveIndex] * change

            if not self.camera.f.ExposureTime.IsWritable():
                print("Unable to set exposure time. Aborting ...")
                return 0
            self.camera.f.ExposureTime.Set(self.get_microseconds(new_exposure))
            print("Exposure changed to:", new_exposure, "when told to change by:", change)
            return new_exposure
        
        except (neoapi.NeoException, Exception) as exc:
            print('Change exposure error:', exc)
            return 0

    def reset_exposure(self):
        """
        Reset the exposure to the original value.
        :param: None
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
        Uninitialize the camera.
        :return: None
        """
        self.camera.AcquisitionStop()
        self.camera.Disconnect()
        del self.camera
        print("Camera un-initialized.")


# making sure that the buffer will have the correct size to this usage.
class MyBuffer(neoapi.BufferBase):
    """implementation for user buffer mode"""
    def __init__(self, size):
        neoapi.BufferBase.__init__(self)
        self._buf = np.zeros(size, np.uint8) if use_numpy else bytearray(size) 
        self._size = size # size of the memory
        self.RegisterMemory(self._buf, self._size)
        self.myContent = 1 # saving on the buffer just one image

    def CalcVar(self):
        var = -1
        if (use_numpy): # buf contains the image data and can be used with numpy
            var = self._buf.var()
        return var