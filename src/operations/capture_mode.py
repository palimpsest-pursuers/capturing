from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
from tifffile import imsave

class CaptureMode(Operation):
    """
    """
    ui = None
    text = "Capturing Image"

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.ui.TopRightLabel.setVisible(True)
        self.ui.LargeDisplay.setVisible(True)
        self.ui.middleRightDisplay.setVisible(True)
        self.ui.infobox.clear()
        self.ui.infobox.setText(self.text)

        self.ui.thread = QThread()
        self.ui.worker = CaptureWorker()
        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.worker.ui = self.ui

        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.sharedFrame.connect(self.updateFrame)
        self.ui.worker.zoomedFrame.connect(self.updateZoomed)
        self.ui.worker.wavelength.connect(self.updateWavelength)

        self.ui.thread.start()

    def cancel(self):
        """"""
        self.ui.worker.cancelled = True
        self.ui.infobox.setText('Operation Canceled')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
        self.ui.TopRightLabel.setVisible(False)
        self.ui.change_operation(self.ui.idle_op)

    def updateFrame(self, n):
        print(type(n))
        pixmap = n 
        self.ui.LargeDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))
        #self.ui.middleRightDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))

    def updateZoomed(self, n):
        print(type(n))
        pixmap = n 
        self.ui.middleRightDisplay.setPixmap(pixmap.scaled(960,540, Qt.KeepAspectRatio))

    def updateWavelength(self, wavelength):
        self.ui.infobox.setText(self.text + "\n" + wavelength)

    '''def finished(self):
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)'''

class CaptureWorker(QObject):
    sharedFrame = pyqtSignal(QPixmap)
    zoomedFrame = pyqtSignal(QPixmap)
    wavelength = pyqtSignal(str)
    cancelled = False
    ui = None

    def run(self):
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11]) #630 nm (red)

        # Choose destination directory
        destination_dir = QFileDialog.getExistingDirectory()

        # Initialize the camera
        self.ui.camera_control.initialize_camera()
        
        i = 0

        for wavelength in self.ui.led_control.wavelength_list:
            print(destination_dir)
            if self.cancelled:
                break
            self.wavelength.emit(wavelength)
            self.ui.led_control.turn_on(wavelength)

            frame = self.ui.camera_control.capture()
            img = self.ui.camera_control.convert_nparray_to_QPixmap(frame)
            
            zoom = self.ui.camera_control.zoom(frame,float(4.0))
            zImg = self.ui.camera_control.convert_nparray_to_QPixmap(zoom)
            self.zoomedFrame.emit(zImg)
            self.sharedFrame.emit(img)

            #save image
            imsave(f"capture-{i:02d}.tiff", frame)

            #time.sleep(0.5) # 500 ms
            i += 1
            
        self.ui.camera_control.uninitialize_camera()
        self.ui.led_control.turn_off()
        self.ui._current_op.finished()