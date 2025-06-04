from controllers.camera_interface import CameraInterface

try:
    from pixelinkWrapper import *
except Exception:
    pass
import numpy as np
import sys


'''
Pixilink Camera Controller 
Written by Sai Keshav Sasanapuri, Cecelia Ahrens, and Robert Maron 
'''


class PixilinkController(CameraInterface):
    hCamera = None
    frame = None

    '''Initialize the camera'''

    def __init__(self):
        try:
            self.ORIGINAL_EXPOSURE = 0.7
            self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16
            self.hCamera = None
            self.acquisition_mode = "Continuous"
            self.frame = None

            # initialize camera
            ret = self.initialize_camera()
            if ret["Success"]:
                # set inital exposure
                ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE)
                if not (PxLApi.apiSuccess(ret[0])):
                    self.uninitialize_camera()
                    return

                params = ret[2]

                params[0] = self.ORIGINAL_EXPOSURE

                ret = PxLApi.setFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE, PxLApi.FeatureFlags.MANUAL, params)
                if not PxLApi.apiSuccess(ret[0]):
                    return
            else:
                raise ValueError("Pixelink camera initialization failed")
        except Exception:
            raise ValueError("Pixelink camera initialization failed")

    '''Function to Initialize camera'''

    def initialize_camera(self):
        try:
            if self.check_camera_initialized():
                return {"Success": True, "Error": None}

            ret = PxLApi.initialize(0)
            if not (PxLApi.apiSuccess(ret[0])):
                raise ValueError("Initialization error")

            # self.exposure = 1
            self.hCamera = ret[1]

            # get proper camera size, create frame from that
            ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.ROI)
            params = ret[2]
            roiWidth = params[PxLApi.RoiParams.WIDTH]
            roiHeight = params[PxLApi.RoiParams.HEIGHT]

            self.frame = np.zeros([int(roiHeight), int(roiWidth)], dtype=np.uint8)

            # Start the stream
            PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.START)
            return {"Success": True, "Error": None}
        except Exception:
            self.uninitialize_camera()
            return {"Success": False, "Error": ex}

    def check_camera_initialized(self) -> bool:
        if self.hCamera is None:
            self.uninitialize_camera()
            return False
        ret, numCameras = PxLApi.getNumberCameras()
        if not PxLApi.apiSuccess(ret) or numCameras == 0:
            self.uninitialize_camera()
            return False
        return True

    def change_acquisition_mode(self, mode: str) -> None:
        self.acquisition_mode = mode

    def Begin_Acquisition(self):
        PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.START)

    def End_Acquisition(self):
        PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.STOP)

    '''Capture an image'''

    def capture(self):
        """
        Captures an image from the camera.
        :return: Numpy array representing the captured image
        """
        if not self.check_camera_initialized():
            return {"Success": False, "Image": None}

        ret = self.get_next_frame(5)

        # frame was successful
        if PxLApi.apiSuccess(ret[0]):
            # update frame
            return {"Success": True, "Image": self.frame}

        # frame was unsuccessful
        else:
            return {"Success": False, "Image": None}

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
                return ret
            else:
                # If the streaming is turned off, or worse yet -- is gone?
                # If so, no sense in continuing.
                if PxLApi.ReturnCode.ApiStreamStopped == ret[0] or \
                        PxLApi.ReturnCode.ApiNoCameraAvailableError == ret[0]:
                    return ret

        # Ran out of tries, so return whatever the last error was.
        return ret

    '''Capture an image at initial exposure multiplied by "exposure" '''

    def capture_at_exposure(self, exposure, waveIndex):
        if self.change_exposure(exposure, waveIndex) == 0:
            return
        return self.capture()

    '''Change camera exposure'''

    def change_exposure(self, change, waveIndex):
        # get exposure
        ret = PxLApi.getFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE)
        if not (PxLApi.apiSuccess(ret[0])):
            return 0

        params = ret[2]
        new_exposure = self.selected_exposure_array[waveIndex] * change

        params[0] = new_exposure

        # set new exposure
        ret = PxLApi.setFeature(self.hCamera, PxLApi.FeatureId.EXPOSURE, PxLApi.FeatureFlags.MANUAL, params)
        if not PxLApi.apiSuccess(ret[0]):
            return 0
        return new_exposure

    '''Reset camera exposure'''

    def reset_exposure(self):
        self.selected_exposure_array = [self.ORIGINAL_EXPOSURE] * 16

    '''Save camera exposure for given band'''

    def save_exposure(self, change, waveIndex):
        self.selected_exposure_array[waveIndex] = change * self.selected_exposure_array[waveIndex]

    '''Save camera exposure for all bands'''

    def save_all_exposures(self, change):
        for i in range(len(self.selected_exposure_array)):
            self.selected_exposure_array[i] *= change

    '''Un-initialize camera'''

    def uninitialize_camera(self):
        # turn off stream state
        try:
            ret = PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.STOP)
            assert PxLApi.apiSuccess(ret[0]), "setStreamState with StreamState.STOP failed"
        except Exception:
            pass
        try:
            if self.hCamera is not None:
                ret = PxLApi.uninitialize(self.hCamera)
                self.hCamera = None
                assert PxLApi.apiSuccess(ret[0]), "un-initialize failed"
        except Exception:
            pass
