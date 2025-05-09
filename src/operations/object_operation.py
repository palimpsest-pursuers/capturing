from operations.operation import Operation
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import numpy as np

'''
Object Operation for Capturing Raw Images of an Object
Written by Cecelia Ahrens, Mallory Bridge, and Robert Maron, Sai Keshav Sasanapuri
'''


class ObjectOp(Operation):
    main = None  # the UI

    '''Start of Object Operation'''

    def on_start(self):
        self.main.thread = QThread()
        self.main.worker = CaptureWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.main.thread.started.connect(self.main.worker.run)

        # connects functions to pyqtSignals
        self.main.worker.sharedFrame.connect(self.updateFrame)
        self.main.worker.zoomedFrame.connect(self.updateZoomed)
        self.main.worker.wavelength.connect(self.updateWavelength)
        self.main.worker.histogram.connect(self.updateHistogram)
        self.main.worker.progress.connect(self.updateProgressBar)
        self.main.worker.finished.connect(self.finished)
        self.main.worker.progress_signal.connect(self.updateProgressDialog)
        self.main.worker.message_signal.connect(self.showMessageBox)
        self.main.worker.end_operation.connect(self.end_operation_midway)

        # initializes progress bar
        self.main.objectProgressBar.setRange(0, 16)
        self.main.objectProgressBar.setValue(0)

        # clears out prev image data
        self.main.cube_builder.img_array = []
        self.main.cube_builder.final_array = []

        # starts worker
        try:
            self.main.thread.start()
        except:
            pass

    '''Cancels Object Operation'''

    def cancel(self):
        """"""
        self.main.worker.cancelled = True
        QObject.deleteLater(self.main.worker)
        self.main.thread.quit()
        self.main.led_control.turn_off()
        self.main.objectStartCaptureButton.setEnabled(True)
        self.main.cube_builder.img_array = []
        self.main.cube_builder.final_array = []

    '''Stop camera feed and start object capture'''
    def startObjectCapture(self):
        self.main.worker.startObjectCapture = True

    '''Finishes Object Operation and goes to review page'''

    def finished(self):
        self.main.thread.quit()
        self.main.objectStartCaptureButton.setEnabled(True)
        self.main.setPage(self.main.objectSteps, self.main.objectStep2)
        self.main.objectDisplay(0)

    '''end process due to error encountered'''

    def end_operation_midway(self, err_msg):
        self.main.progress_box.start("Cancelling Operation")
        self.main.camera_control.uninitialize_camera()
        self.main.progress_box.stop()
        self.main.message_box.show_error(message=err_msg)
        self.main.cancelOp(self.main.objectSteps, self.main.objectStep0, self.main.object_op)

    '''Create and show message box'''

    def showMessageBox(self, msg_type, message):
        if msg_type == 'info':
            self.main.message_box.show_info(message=message)
        elif msg_type == 'warning':
            self.main.message_box.show_warning(message=message)
        elif msg_type == 'error':
            self.main.message_box.show_error(message=message)
        elif msg_type == 'question':
            return self.main.message_box.show_question(message=message)

    '''Start or Stop Progress dialog box'''

    def updateProgressDialog(self, message):
        if message == "close":
            self.main.progress_box.stop()
        else:
            self.main.progress_box.start(message)

    '''Updates main display'''

    def updateFrame(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.objectstep1View.width() - 14, self.main.objectstep1View.height() - 14,
                                   QtCore.Qt.KeepAspectRatio))
        self.main.objectstep1View.setScene(scene)

    '''Updates smaller display for zoomed in image'''

    def updateZoomed(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(
            img.scaled((self.main.objectStep1Zoom.width() * 2) - 14, (self.main.objectStep1Zoom.height() * 2) - 14,
                       QtCore.Qt.KeepAspectRatio))
        self.main.objectStep1Zoom.setScene(scene)

    '''Updates histogram'''

    def updateHistogram(self, hist):
        scene = QtWidgets.QGraphicsScene()

        # Determine the width and height of the scene
        width = self.main.objectStep1Hist.width() - 14
        height = self.main.objectStep1Hist.height() - 14

        # Create a QGraphicsRectItem object for each histogram bar
        bar_width = width / len(hist)
        max_height = max(hist)
        for i, value in enumerate(hist):
            bar_height = height * value / max_height
            bar = QtWidgets.QGraphicsRectItem(i * bar_width, height - bar_height, bar_width, bar_height)
            scene.addItem(bar)

        self.main.objectStep1Hist.setScene(scene)

    '''Updates wavelength label'''

    def updateWavelength(self, wavelength):
        self.main.objectStep1Wave.setText("Wavelength: " + wavelength)

    '''Updates progress bar'''

    def updateProgressBar(self, value):
        self.main.objectProgressBar.setValue(value)

    '''Updates the exposure display box with current exposures'''
    def updateExposureDisplay(self):
        ExposureText = ""
        exposure_values = self.main.camera_control.selected_exposure_array
        for i, value in enumerate(exposure_values, start=1):
            value = round((value/0.7)*100)
            ExposureText += f"{i} - {value}\n"
        self.main.ExposureDispText.setText(ExposureText)


class CaptureWorker(QObject):
    sharedFrame = pyqtSignal(QPixmap)
    zoomedFrame = pyqtSignal(QPixmap)
    wavelength = pyqtSignal(str)
    histogram = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int)
    progress_signal = pyqtSignal(str)
    message_signal = pyqtSignal(str, str)
    end_operation = pyqtSignal(str)
    cancelled = False
    startObjectCapture = False
    finished = pyqtSignal()
    main = None

    def run(self):
        self.progress_signal.emit("Starting camera live feed")

        # check if camera is initialized
        if not self.main.check_if_camera_is_initialized()["Success"]:
            ret = self.main.initialize_cameras()
            if not ret["Success"]:
                self.progress_signal.emit("close")
                self.end_operation.emit("Failed to connect to camera. Ensure wired connection and try again.")
                return

        self.main.led_control.turn_on(self.main.led_control.wavelength_list[8])
        # change acquisition mode to continuous
        if self.main.camera_control.acquisition_mode != 'Continuous':
            self.main.camera_control.change_acquisition_mode(mode='Continuous')
        self.main.camera_control.change_exposure(self.main.camera_control.exposureArray[8], 8)
        self.main.camera_control.camera.BeginAcquisition()
        self.progress_signal.emit("close")
        
        while not self.cancelled and not self.startObjectCapture:
            ret = self.main.camera_control.capture()
            if not ret["Success"]:
                self.end_operation.emit("Image acquisition failed")
                return
            frame = ret["Image"]
            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
            self.sharedFrame.emit(img)

        self.main.camera_control.camera.EndAcquisition()
        self.main.led_control.turn_off()
        self.main.objectStartCaptureButton.setEnabled(False)
        
        if not self.cancelled:
            self.progress_signal.emit("Starting Capture")
            # change acquisition mode to single frame
            if self.main.camera_control.acquisition_mode != 'SingleFrame':
                self.main.camera_control.change_acquisition_mode(mode='SingleFrame')
            # grab test image. First image is sometimes funky
            self.main.camera_control.camera.BeginAcquisition()
            self.main.camera_control.capture_at_exposure(self.main.camera_control.exposureArray[0], 0)
            self.main.camera_control.camera.EndAcquisition()
            self.progress_signal.emit("close")

            # Captures an image at every wavelength
            for i in range(0, len(self.main.led_control.wavelength_list)):
                # check if camera is initialized
                if not self.main.check_if_camera_is_initialized()["Success"]:
                    ret = self.main.initialize_cameras()
                    if not ret["Success"]:
                        self.progress_signal.emit("close")
                        self.end_operation.emit("Failed to connect to camera. Ensure wired connection and try again.")
                        return

                if self.cancelled:
                    return
                wavelength = self.main.led_control.wavelength_list[i]
                self.wavelength.emit(wavelength)
                self.main.led_control.turn_on(wavelength)

                self.main.camera_control.camera.BeginAcquisition()
                ret = self.main.camera_control.capture_at_exposure(self.main.camera_control.exposureArray[i], i)
                self.main.camera_control.camera.EndAcquisition()
                if not ret["Success"]:
                    self.progress_signal.emit("close")
                    self.end_operation.emit("Image acquisition failed")
                    return
                frame = ret["Image"]

                img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
                self.sharedFrame.emit(img)

                histogram, bins = np.histogram(frame, bins=20, range=(0, 255))  # use 20 bins and a range of 0-255
                self.histogram.emit(histogram)

                self.zoomedFrame.emit(img)
                self.main.cube_builder.add_raw_image(frame, wavelength)  # save image
                self.main.led_control.turn_off()
                self.progress.emit(i + 1)
                i += 1
            self.main.led_control.turn_off()
            if not self.cancelled:
                self.finished.emit()

