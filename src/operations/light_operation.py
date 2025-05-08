from operations.operation import Operation
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

'''
Light Operation for Setting the Exposure of the Pixilink Camera
Written by Cecelia Ahrens, Sai Keshav Sasanapuri
'''


class LightOp(Operation):
    main = None
    exposure1 = 1
    exposure2 = 0.66
    exposure3 = 1.5
    exposure4 = 2
    waveIndex = None
    size = None

    '''Starts Light Operation'''

    def on_start(self, waveIndex):
        # start thread, move worker to thread
        self.waveIndex = waveIndex
        self.main.thread = QThread()
        self.main.worker = ExposureWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.size = self.main.lightLevel0.size()

        self.main.thread.started.connect(self.main.worker.run)

        # disable select light level buttons until all snapshots have been taken
        self.main.lightLevel0.setEnabled(False)
        self.main.lightLevel1.setEnabled(False)
        self.main.lightLevel2.setEnabled(False)
        self.main.lightLevel3.setEnabled(False)

        # connect slots
        self.main.worker.img1.connect(self.tl_display)
        self.main.worker.img2.connect(self.tr_display)
        self.main.worker.img3.connect(self.bl_display)
        self.main.worker.img4.connect(self.br_display)
        self.main.worker.captureStatus.connect(self.updateStatus)
        self.main.worker.finished.connect(self.finished)
        self.main.worker.progress_signal.connect(self.updateProgressDialog)
        self.main.worker.message_signal.connect(self.showMessageBox)
        self.main.worker.end_operation.connect(self.end_operation_midway)

        self.main.thread.start()

    '''end process due to error encountered'''

    def end_operation_midway(self, err_msg):
        self.main.progress_box.start("Cancelling Operation")
        self.main.camera_control.uninitialize_camera()
        self.main.lightCancelButtonClicked()
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

    '''Cancel Light Operation'''

    def cancel(self):
        self.main.useExistingExposuresButton.setEnabled(False)
        self.main.camera_control.reset_exposure()
        self.main.worker.cancelled = True
        self.main.thread.quit()
        self.main.led_control.turn_off()

    '''Finish light operation and allow the user to select light level'''

    def finished(self):
        self.main.thread.quit()
        self.main.led_control.turn_off()
        self.main.lightLevel0.setEnabled(True)
        self.main.lightLevel1.setEnabled(True)
        self.main.lightLevel2.setEnabled(True)
        self.main.lightLevel3.setEnabled(True)

    '''Saves exposure level'''

    def save_level(self, exposure, waveIndex):
        self.main.camera_control.save_exposure(exposure, waveIndex)
        self.finished()

    '''Saves exposure level for all bands'''

    def save_all_levels(self, exposure):
        self.main.camera_control.save_all_exposures(exposure)
        self.finished()

    '''Displays image top left button'''

    def tl_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel0.width() - 24, self.main.lightLevel0.height() - 24)
        self.main.lightLevel0.setIconSize(size)
        self.main.lightLevel0.setIcon(icon)

    '''Displays image in top right button'''

    def tr_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel1.width() - 24, self.main.lightLevel1.height() - 24)
        self.main.lightLevel1.setIconSize(size)
        self.main.lightLevel1.setIcon(icon)

    '''Displays image in bottom left button'''

    def bl_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel2.width() - 24, self.main.lightLevel2.height() - 24)
        self.main.lightLevel2.setIconSize(size)
        self.main.lightLevel2.setIcon(icon)

    '''Displays image in bottom right button'''

    def br_display(self, img):
        icon = QIcon(img)
        size = QSize(self.main.lightLevel3.width() - 24, self.main.lightLevel3.height() - 24)
        self.main.lightLevel3.setIconSize(size)
        self.main.lightLevel3.setIcon(icon)

    '''Update which led is capturing'''

    def updateStatus(self, s):
        self.main.lightPageTitle.setText(f"{s}")

    '''Save exposure profile'''

    def saveProfile(self, file_name, destination_dir=None):
        if destination_dir is None:
            try:
                destination_dir = QFileDialog.getExistingDirectory()
            except:
                pass
        if file_name == "Enter File Name":
            file_name = "ExposureProfile"
        file_name = file_name.strip()
        if destination_dir is not None and file_name:
            exposureProfile = [(x / 0.7) * 100 for x in self.main.camera_control.selected_exposure_array]
            destination_dir = os.path.join(destination_dir, f'{file_name}.txt')
            # Save the array to the specified file as space-separated values
            with open(destination_dir, 'w') as file:
                file.write(' '.join(map(str, exposureProfile)))

    '''Load exposure profile'''

    def loadProfile(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(filter='Text Files (*.txt)')
        except:
            pass
        if file_path is not None and file_path != "":
            with open(file_path, 'r') as file:
                file_contents = file.read()
                isValid, exposureProfile = self.validateFile(file_contents)
                if isValid:
                    try:
                        exposureProfile = [float(value) for value in file_contents.split()]
                        self.main.camera_control.selected_exposure_array = [(x / 100) * 0.7 for x in exposureProfile]
                        return True
                    except:
                        self.main.camera_control.reset_exposure()
                self.main.lightPageTitle.setText("Failed to load Exposure Profile")
                return False

    '''Validates the exposure profile file'''

    def validateFile(self, contents):
        values = contents.split()
        if len(values) == 16:
            try:
                data = [float(value) for value in values]
                if all(value >= 0 for value in data):
                    return True, data
                else:
                    return False, "Invalid File"
            except ValueError:
                return False, "Invalid File"
        else:
            return False, "Invalid File"



class ExposureWorker(QObject):
    img1 = pyqtSignal(QPixmap)
    img2 = pyqtSignal(QPixmap)
    img3 = pyqtSignal(QPixmap)
    img4 = pyqtSignal(QPixmap)
    captureStatus = pyqtSignal(str)
    finished = pyqtSignal()
    progress_signal = pyqtSignal(str)
    message_signal = pyqtSignal(str, str)
    end_operation = pyqtSignal(str)
    waveIndex = None
    cancelled = False
    main = None

    def run(self):
        # check if camera is initialized
        self.progress_signal.emit("Starting Camera")
        if not self.main.check_if_camera_is_initialized()["Success"]:
            ret = self.main.initialize_cameras()
            if not ret["Success"]:
                self.progress_signal.emit("close")
                self.end_operation.emit("Failed to connect to camera. Ensure wired connection and try again.")
                return

        # change acquisition mode to single frame
        if self.main.camera_control.acquisition_mode != 'SingleFrame':
            self.main.camera_control.change_acquisition_mode(mode='SingleFrame')

        self.progress_signal.emit("Acquiring Images")
        self.waveIndex = self.main.light_op.waveIndex
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[self.waveIndex])
        self.captureStatus.emit(
            "Capturing Exposure levels at wavelength " + self.main.led_control.wavelength_list[self.waveIndex]
            + " - (" + str(self.waveIndex + 1) + "/16)")

        # Take photo at x1 exposure
        self.main.camera_control.camera.BeginAcquisition()
        ret = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure1 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.main.camera_control.camera.EndAcquisition()
        if not ret["Success"]:
            self.progress_signal.emit("close")
            self.end_operation.emit("Image acquisition failed")
            return
        frame1 = ret["Image"]
        self.img1.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame1))
        if self.cancelled:
            return

        # Take photo at x0.66 exposure
        self.main.camera_control.camera.BeginAcquisition()
        ret = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure2 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.main.camera_control.camera.EndAcquisition()
        if not ret["Success"]:
            self.progress_signal.emit("close")
            self.end_operation.emit("Image acquisition failed")
            return
        frame2 = ret["Image"]
        self.img2.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame2))
        if self.cancelled:
            return

        # Take photo at x1.5 exposure
        self.main.camera_control.camera.BeginAcquisition()
        ret = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure3 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.main.camera_control.camera.EndAcquisition()
        if not ret["Success"]:
            self.progress_signal.emit("close")
            self.end_operation.emit("Image acquisition failed")
            return
        frame3 = ret["Image"]
        self.img3.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame3))
        if self.cancelled:
            return

        # Take photo at x2 exposure
        self.main.camera_control.camera.BeginAcquisition()
        ret = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure4 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.main.camera_control.camera.EndAcquisition()
        if not ret["Success"]:
            self.progress_signal.emit("close")
            self.end_operation.emit("Image acquisition failed")
            return
        frame4 = ret["Image"]
        self.img4.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame4))
        if self.cancelled:
            return

        self.progress_signal.emit("close")
        self.finished.emit()
        self.captureStatus.emit(
            "Select Exposure level for wavelength " + self.main.led_control.wavelength_list[self.waveIndex]
            + " - (" + str(self.waveIndex + 1) + "/16)")
