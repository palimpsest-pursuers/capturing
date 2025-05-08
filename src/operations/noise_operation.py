from operations.operation import Operation
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

'''
Noise Operation for Capturing Raw Noise Image
Written by Cecelia Ahrens, and Robert Maron
'''


class NoiseOp(Operation):
    main = None
    img = None

    '''Starts Noise Operation'''

    def on_start(self) -> None:
        # UI stuff to prevent errors 
        self.main.noiseContinueButton.setEnabled(False)
        self.main.noiseRetakeButton.setEnabled(False)
        self.main.noiseView.setHidden(True)

        # creates and sets main thread and capture worker
        self.main.thread = QThread()
        self.main.worker = NoiseWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.main.thread.started.connect(self.main.worker.run)

        # connects functions to pyqtSignals
        self.main.worker.imgView.connect(self.updateNoiseView)
        self.main.worker.finished.connect(self.finished)
        self.main.worker.progress_signal.connect(self.updateProgressDialog)
        self.main.worker.message_signal.connect(self.showMessageBox)
        self.main.worker.end_operation.connect(self.end_operation_midway)

        self.main.cube_builder.noise = []  # clears noise image array

        # starts worker 
        self.main.thread.start()

    '''Update Main Noise Display'''

    def updateNoiseView(self, img):
        scene = QtWidgets.QGraphicsScene()
        self.main.noiseView.setScene(scene)
        self.main.noiseView.setHidden(False)
        scene.addPixmap(
            img.scaled(self.main.noiseView.width(), self.main.noiseView.height(), QtCore.Qt.KeepAspectRatio))

    '''end process due to error encountered'''

    def end_operation_midway(self, err_msg):
        self.main.progress_box.start("Cancelling Operation")
        self.main.camera_control.uninitialize_camera()
        self.main.progress_box.stop()
        self.main.message_box.show_error(message=err_msg)
        self.main.cancelOp(self.main.noiseSteps, self.main.noiseStep0, self.main.noise_op)

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

    '''Finish Noise Operation'''

    def finished(self):
        self.main.noiseContinueButton.setEnabled(True)
        self.main.noiseRetakeButton.setEnabled(True)
        self.main.thread.quit()

    def save(self):
        pass

    '''Cancel Noise Operation'''

    def cancel(self):
        self.main.thread.quit()
        self.main.cube_builder.noise = []
        self.main.useExistingNoiseButton.setEnabled(False)


class NoiseWorker(QObject):
    imgView = pyqtSignal(QPixmap)
    finished = pyqtSignal()
    progress_signal = pyqtSignal(str)
    message_signal = pyqtSignal(str, str)
    end_operation = pyqtSignal(str)
    main = None

    def run(self):
        # capture a single image
        self.progress_signal.emit("Starting Camera")
        # check if camera is initialized
        if not self.main.check_if_camera_is_initialized()["Success"]:
            ret = self.main.initialize_cameras()
            if not ret["Success"]:
                self.progress_signal.emit("close")
                self.end_operation.emit("Failed to connect to camera. Ensure wired connection and try again.")
                return
        # change acquisition mode to single frame
        if self.main.camera_control.acquisition_mode != 'SingleFrame':
            self.main.camera_control.change_acquisition_mode(mode='SingleFrame')
        self.progress_signal.emit("Capturing noise")
        self.main.camera_control.camera.BeginAcquisition()
        ret = self.main.camera_control.capture()
        self.main.camera_control.camera.EndAcquisition()
        if not ret["Success"]:
            self.progress_signal.emit("close")
            self.end_operation.emit("Image acquisition failed")
            return

        frame = ret["Image"]
        img = self.main.camera_control.convert_nparray_to_QPixmap(frame)
        self.imgView.emit(img)
        self.progress_signal.emit("Success!")
        self.main.cube_builder.add_noise_image(frame)
        self.finished.emit()
        self.progress_signal.emit("close")
