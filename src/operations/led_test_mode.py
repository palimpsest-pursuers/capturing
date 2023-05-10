from itertools import cycle
import time
from threading import Thread
from operations.operation import Operation
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt, pyqtSlot
import debugpy

'''
Test LED Operation for Flashing Visible Light From LEDs
Written by Cecelia Ahrens, and Mallory Bridge 
'''
class TestLEDMode(Operation):
    main = None
    cancelled = False

    '''Starts Test LEDs Operation'''
    def on_start(self, mainWindow):
        #start thread, move worker to thread
        self.main.thread = QThread(mainWindow)
        self.main.worker = LEDWorker()
        self.main.worker.main = self.main
        self.main.worker.moveToThread(self.main.thread)
        self.main.thread.started.connect(self.main.worker.run)

        # connect slots
        self.main.worker.wavelength.connect(self.update_text)
        self.main.worker.finished.connect(self.finished)

        # update UI info text
        self.main.startingInfo.setText("Testing LEDs")

        #start
        self.main.thread.start()

    '''Update UI text with current wavelength'''
    def update_text(self, text):
        self.main.startingInfo.setText("Testing LEDs!\n\nFlashing wavelength: "+text)

    '''Cancel Operation'''
    def cancel(self):
        self.main.worker.cancelled = True

    '''Finish Operation'''
    def finished(self):
        self.main.led_control.turn_off()
        self.main.thread.quit()
        self.main.cancelLEDsButton.setEnabled(False)
        self.main.testLEDsButton.setEnabled(True)
        self.main.startingInfo.setText(self.main.intro_text)
        self.main.testLEDsButton.setText("Test LEDs")


class LEDWorker(QObject):
    wavelength = pyqtSignal(str)
    finished = pyqtSignal()
    cancelled = False

    main = None

    def run(self):
        # Only cycle through the wavelengths that are visible
        for wavelength in self.main.led_control.wavelength_list[4:12]:
            self.main.led_control.turn_on(wavelength)
            self.wavelength.emit(wavelength)
            i = 0
            while (i <= 1 and not self.cancelled):
                time.sleep(0.1)
                i = i + 0.1
            self.main.led_control.turn_off()
            if self.cancelled:
                break
            
        self.finished.emit()
