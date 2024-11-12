"""
Baumer Camera controller
Writen by Julia Schenatto (IFUSP)
"""

import sys
use_numpy = False
import time
try:
    import numpy as np
    use_numpy = True
except ImportError:
    pass
from controllers.camera_interface import CameraInterface
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
            if not self.camera.f.ExposureAuto.IsWritable():
                print("Auto exposure cannot be modified.")
            self.camera.f.ExposureMode.Set(neoapi.ExposureMode_Timed)
            self.camera.f.ExposureAuto.Set(neoapi.ExposureAuto_Off)  # Disable AutoExposure
            print("Auto exposure disabled.")

            # Configure exposure time
            self.camera.f.ExposureTime.Set(self.get_microseconds(self.ORIGINAL_EXPOSURE))
            print("Exposure set to:", self.ORIGINAL_EXPOSURE)

            # Disable automatic gain
            if self.camera.f.GainAuto.IsWritable():
                self.camera.f.GainAuto.Set(neoapi.GainAuto_Off)
                print("Automatic gain disabled.")

            self.uninitialize_camera()

        except (neoapi.NeoException, Exception) as exc:
            print('Error:', exc)
            raise #ValueError("Camera initialization failed")
        except Exception as e:
            print(e)

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

            if not self.camera.IsConnected():
                print("Camera not initialized.")
                raise ValueError("No cameras found during initialization")

            if self.camera.f.AcquisitionMode.IsWritable():
                self.camera.f.AcquisitionMode.Set(neoapi.AcquisitionMode_Continuous) # ou outro modo desejado
                print ("AcquisitionMode changed to Continuous")
            else:
                print("Unable to change the AcquisitionMode")
                raise

            self.camera.StartStreaming()
            print('Baumer camera initialized.')
            # no list necessary, by the looks of the python wrapper from Baumer.
            ####################################################

        except (neoapi.NeoException, Exception) as exc:
            print('Initialization error:', exc)
            raise ValueError("Baumer Blackfly initialization failed")
        except Exception as e:
            print(e)

    def capture(self):
        """Capture an image from the camera."""
        try:
            if not self.camera.IsConnected():
                print("Camera not initialized.")
                return None

            self.camera.StartStreaming()

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

            # Verify the shape of the image
            #print(f"Image shape: {image_numpy.shape}")
            # Verificar se a imagem é válida
            if image_numpy is None or image_numpy.size == 0 or image_numpy.shape[0] == 0 or image_numpy.shape[1] == 0:
                print("Captured image has invalid size:", image_numpy.shape)
                return None

            #print(f"Min value: {np.min(image_numpy)}, Max value: {np.max(image_numpy)}")

            # Removing the extra dimension for a monocromatic camera (width, height, 1)
            if image_numpy.shape[-1] == 1:
                image_numpy = np.squeeze(image_numpy, axis=-1)
                print(f"Squeezed image shape: {image_numpy.shape}")

            # Rotate image 180 degrees
            image_numpy = np.rot90(image_numpy, 2)

            # Verificação adicional antes de normalizar e calcular o gradiente
            if np.max(image_numpy) == np.min(image_numpy):
                print("Image has uniform pixel values, cannot normalize.")
                return None

            # Normalize the image
            image_normalized = (image_numpy - np.min(image_numpy)) / (np.max(image_numpy) - np.min(image_numpy))

            # Verifing the size of the array before calculating the gradient
            #print(f"Normalized image shape: {image_normalized.shape}")
            if image_normalized.shape[0] < 2 or image_normalized.shape[1] < 2:
                print("Image is too small to calculate gradient:", image_normalized.shape)
                return None

            fx, fy = np.gradient(image_normalized * 255)

            # Find maximum sharpness
            self.sharpness = np.max([np.max(fx), np.max(fy)])
            print("Sharpness:", self.sharpness)

            # Clear image buffer
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
        try:
            self.camera.StopStreaming()
            self.camera.Disconnect()
            del self.camera
            print("Camera un-initialized.")

        except (neoapi.NeoException, Exception) as exc:
            print('Change exposure error:', exc)
            return 0


# making sure that the buffer will have the correct size to this usage.
class MyBuffer(neoapi.BufferBase):
    """implementation for user buffer mode"""
    def __init__(self, size):
        neoapi.BufferBase.__init__(self)
        self._buf = np.zeros(size, np.uint8) if use_numpy else bytearray(size)
        self._size = size # size of the memory
        self.RegisterMemory(self._buf, self._size)
        self.myContent = 5 # saving on the buffer just one image

    def CalcVar(self):
        var = -1
        if (use_numpy): # buf contains the image data and can be used with numpy
            var = self._buf.var()
        return var