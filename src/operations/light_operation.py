from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
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

        self.main.thread.start()

    '''Cancel Light Operation'''

    def cancel(self):
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
        # print(self.main.camera_control.exposure)
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
                    exposureProfile = [float(value) for value in file_contents.split()]
                    self.main.camera_control.selected_exposure_array = [(x / 100) * 0.7 for x in exposureProfile]
                    return True
                else:
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
                    print("Invalid values. All values should be non-negative.")
                    return False, "Invalid File"
            except ValueError:
                print("Invalid values. All values should be numeric.")
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
    waveIndex = None
    cancelled = False
    main = None

    def run(self):
        self.waveIndex = self.main.light_op.waveIndex
        self.main.led_control.turn_on(self.main.led_control.wavelength_list[self.waveIndex])
        self.captureStatus.emit(
            "Capturing Exposure levels at wavelength " + self.main.led_control.wavelength_list[self.waveIndex]
            + " - (" + str(self.waveIndex + 1) + "/16)")
        # Initialize the camera
        self.main.camera_control.initialize_camera()

        # Take photo at x1 exposure
        self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure1 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        frame1 = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure1 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.img1.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame1))
        self.main.camera_control.uninitialize_camera()
        if self.cancelled:
            self.main.resetDisplay()
            return

        # Take photo at x0.66 exposure
        self.main.camera_control.initialize_camera()
        self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure2 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        frame2 = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure2 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.img2.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame2))
        self.main.camera_control.uninitialize_camera()
        if self.cancelled:
            self.main.resetDisplay()
            return

        # Take photo at x1.5 exposure
        self.main.camera_control.initialize_camera()
        self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure3 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        frame3 = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure3 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.img3.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame3))
        self.main.camera_control.uninitialize_camera()
        if self.cancelled:
            self.main.resetDisplay()
            return

        # Take photo at x2 exposure
        self.main.camera_control.initialize_camera()
        self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure4 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        frame4 = self.main.camera_control.capture_at_exposure(
            self.main.light_op.exposure4 * self.main.camera_control.exposureArray[self.waveIndex], self.waveIndex)
        self.img4.emit(self.main.camera_control.convert_nparray_to_QPixmap(frame4))
        self.main.camera_control.uninitialize_camera()
        if self.cancelled:
            self.main.resetDisplay()
            return

        self.finished.emit()
        self.captureStatus.emit(
            "Select Exposure level for wavelength " + self.main.led_control.wavelength_list[self.waveIndex]
            + " - (" + str(self.waveIndex + 1) + "/16)")
        print(1)
