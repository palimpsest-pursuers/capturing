from operations.operation import Operation
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import numpy as np
from threading import Thread
import cv2

'''
Focus Operation for Displaying "Live" Images for Camara Focus Adjustment
Written by Cecelia Ahrens
'''


class FocusOp(Operation):
    main = None

    def on_start(self):
        # start thread, move worker to thread
        self.main.thread = QThread()
        self.main.worker = FocusWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main

        # connect slots
        self.main.thread.started.connect(self.main.worker.run)
        self.main.worker.mainFrame.connect(self.updateFrame)
        self.main.worker.x2Frame.connect(self.update2XZoomed)
        self.main.worker.sharpness.connect(self.updateSharpness)
        self.main.worker.finished.connect(self.finished)
        self.main.worker.progress_signal.connect(self.updateProgressDialog)
        self.main.worker.message_signal.connect(self.showMessageBox)
        self.main.worker.end_operation.connect(self.end_operation_midway)

        self.main.thread.start()

    '''Cancel Operation'''

    def cancel(self):
        self.main.worker.notCancelled = False
        self.main.led_control.turn_off()
        self.main.thread.quit()

    '''Finish Operation'''

    def finished(self):
        self.main.thread.quit()

    '''end process due to error encountered'''

    def end_operation_midway(self, err_msg):
        self.main.progress_box.start("Cancelling Operation")
        self.main.camera_control.uninitialize_camera()
        self.main.progress_box.stop()
        self.main.message_box.show_error(message=err_msg)
        self.main.cancelOp(self.main.focusSteps, self.main.focusStep0, self.main.focus_op)

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

    '''Update zoom factor in focus page of zoom window'''

    def updateZoomFactor(self, value):
        self.main.worker.zoom_factor = value

    '''Update Main Display'''

    def updateFrame(self, img):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(
            img.scaled(self.main.focusView.width(), self.main.focusView.height(), QtCore.Qt.KeepAspectRatio))
        self.main.focusView.setScene(scene)

    '''Update smaller display for X2 zoomed image'''

    def update2XZoomed(self, img, zoom_factor):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img.scaled(self.main.focusStep1Zoom1View.width() * zoom_factor,
                                   self.main.focusStep1Zoom1View.height() * zoom_factor,
                                   QtCore.Qt.KeepAspectRatio))
        self.main.focusStep1Zoom1View.setScene(scene)

    '''Update sharpness label'''

    def updateSharpness(self, n):
        self.main.focusStep1Sharpness.setText(f"Sharpness: {n}")


class FocusWorker(QObject):
    mainFrame = pyqtSignal(QPixmap)
    x2Frame = pyqtSignal(QPixmap, int)
    sharpness = pyqtSignal(int)
    notCancelled = True
    main = None
    zoom_factor = 1
    finished = pyqtSignal()
    progress_signal = pyqtSignal(str)
    message_signal = pyqtSignal(str, str)
    end_operation = pyqtSignal(str)

    def calculate_sharpness(self, numpy_img, method):
        sharpness = 0
        if method == 'gradient':
            # Calculate Sharpness
            # Gradient Method - OG Method
            min_val = np.min(numpy_img)
            max_val = np.max(numpy_img)
            img_normalized = (numpy_img - min_val) / (max_val - min_val)

            # Calculate gradient
            fx, fy = np.gradient(img_normalized * 255)

            sharpness = round(np.max([np.max(fx), np.max(fy)]))

        elif method == 'laplacian':
            # laplacian method
            # The Laplacian operator detects edges by calculating the second derivative of the image intensity.
            # The variance of the Laplacian gives a measure of focus—higher values indicate sharper images
            laplacian = cv2.Laplacian(numpy_img, cv2.CV_64F)
            variance = laplacian.var()

            sharpness = round(variance)

        elif method == 'brenner':
            # Brenner gradient method
            # This method uses differences between adjacent pixels to evaluate sharpness. It is simpler and faster
            shifted = np.roll(numpy_img, -1, axis=1)
            gradient = (numpy_img - shifted) ** 2
            sharpness = round(np.sum(gradient) / 1000000)

        if self.notCancelled:
            self.sharpness.emit(sharpness)

    def run(self):
        self.progress_signal.emit("Starting Camera")

        # check if camera is initialized
        if not self.main.check_if_camera_is_initialized()["Success"]:
            ret = self.main.initialize_cameras()
            if not ret["Success"]:
                self.progress_signal.emit("close")
                self.end_operation.emit("Failed to connect to camera. Ensure wired connection and try again.")
                return

        # change acquisition mode to continuous
        if self.main.camera_control.acquisition_mode != 'Continuous':
            self.main.camera_control.change_acquisition_mode(mode='Continuous')
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[8])
        self.main.camera_control.change_exposure(self.main.camera_control.exposureArray[8], 8)
        frame_no = -1
        self.main.camera_control.camera.BeginAcquisition()
        self.progress_signal.emit("close")

        while self.notCancelled:
            ret = self.main.camera_control.capture()
            if not ret["Success"]:
                self.end_operation.emit("Image acquisition failed")
                return

            frame = ret["Image"]
            frame_no += 1
            img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
            self.mainFrame.emit(img)
            if self.zoom_factor > 1:
                self.x2Frame.emit(img, self.zoom_factor)
            if frame_no % 10 == 0:
                Thread(target=self.calculate_sharpness, args=(frame, 'gradient')).start()

        self.main.camera_control.camera.EndAcquisition()
        self.finished.emit()
