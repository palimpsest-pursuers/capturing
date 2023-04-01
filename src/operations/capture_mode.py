from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
from tifffile import imsave
import numpy as np
import matplotlib.pyplot as plt
from cube_creation.build_cube import CubeBuilder
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
from matplotlib import pyplot as plt

class CaptureMode(Operation):
    """
    """
    ui = None
    text = "Capturing Image"
    cube_builder = CubeBuilder()

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True) 
        self.ui.TopRightWidget.setVisible(True)
        self.ui.LargeDisplay.setVisible(True)
        self.ui.middleRightDisplay.setVisible(True)
        self.ui.infobox.clear()
        self.ui.infobox.setText(self.text)

        self.ui.thread = QThread()
        self.ui.worker = CaptureWorker()
        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.worker.ui = self.ui
        self.ui.worker.cube_builder = self.cube_builder

        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.sharedFrame.connect(self.updateFrame)
        self.ui.worker.zoomedFrame.connect(self.updateZoomed)
        self.ui.worker.wavelength.connect(self.updateWavelength)
        self.ui.worker.histogram.connect(self.updateHistogram)

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

    def updateHistogram(self, data):
        '''figure = Figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.plot(histogram)
        canvas.draw()'''
        '''figure = plt.figure
        #canvas = FigureCanvas(figure)
        plt.hist(data, bins='auto')
        plt.title("Histogram")
        self.ui.TopRightDisplay.setPixmap(figure)
        plt.show()'''
        pass

    '''def finished(self):
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)'''

class CaptureWorker(QObject):
    sharedFrame = pyqtSignal(QPixmap)
    zoomedFrame = pyqtSignal(QPixmap)
    wavelength = pyqtSignal(str)
    histogram = pyqtSignal(np.ndarray)
    cancelled = False
    ui = None
    cube_builder = None
    flats = False

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
            #self.sharedFrame.emit(img)
            #self.ui.led_control.turn_off()
            #histogram = np.histogram(frame)
            #self.histogram.emit(frame)
            
            zoom = self.ui.camera_control.zoom(frame,float(4.0))
            zImg = self.ui.camera_control.convert_nparray_to_QPixmap(zoom)
            self.zoomedFrame.emit(zImg)

            

            #save image
            imsave(f"raw-{wavelength}.tif", frame)

            self.cube_builder.add_raw_image(frame, wavelength)
            #time.sleep(0.5) # 500 ms
            i += 1
        
        if self.flats:
            i = 0
            self.wavelength.emit("REMOVE ARTIFACT!!!")
            time.sleep(10.0)
            for wavelength in self.ui.led_control.wavelength_list:
                print(destination_dir)
                if self.cancelled:
                    break
                self.wavelength.emit(wavelength)
                self.ui.led_control.turn_on(wavelength)

                frame = self.ui.camera_control.capture()

                img = self.ui.camera_control.convert_nparray_to_QPixmap(frame)
                self.sharedFrame.emit(img)
                #self.ui.led_control.turn_off()

                zoom = self.ui.camera_control.zoom(frame,float(4.0))
                zImg = self.ui.camera_control.convert_nparray_to_QPixmap(zoom)
                self.zoomedFrame.emit(zImg)

                #save image
                imsave(f"flat-{wavelength}.tif", frame)

                self.cube_builder.add_flat_image(frame, i)
                #time.sleep(0.5) # 500 ms
                i += 1
        #self.cube_builder.crop(200, 400, 100, 300)
        self.cube_builder.build()
        self.ui.camera_control.uninitialize_camera()
        self.ui.led_control.turn_off()
        self.ui._current_op.finished()