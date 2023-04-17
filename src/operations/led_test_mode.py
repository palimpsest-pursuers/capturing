from itertools import cycle
import time
from threading import Thread
from operations.operation import Operation
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt, pyqtSlot

class TestLEDMode(Operation):
    """
    """
    main = None
    cancelled = False

    def on_start(self, mainWindow):
        """  """
        '''#self.main.CaptureButton.setEnabled(False)
        #self.main.TestLedsButton.setEnabled(False)
        #self.main.FlatsButton.setEnabled(False)
        self.main.FocusButton.setEnabled(False)
        self.main.LightLevelsButton.setEnabled(False)
        self.main.CancelButton.setEnabled(True)'''
        self.main.thread = QThread(mainWindow)
        self.main.worker = LEDWorker()
        self.main.worker.main = self.main
        self.main.worker.moveToThread(self.main.thread)
        self.main.thread.started.connect(self.main.worker.cycle_wavelengths)
        self.main.worker.wavelength.connect(self.update_text)
        self.main.worker.finished.connect(self.finished)
        self.main.startingInfo.setText("Testing LEDs")
        #self.ui.TopRightLabel.setVisible(False)
        #thread = Thread(target=self.cycle_wavelengths())
        #thread.run()
        #self.cycle_wavelengths()
        self.main.thread.start()
        #self.main.thread.wait()

    def update_text(self, text):
        self.main.startingInfo.setText(text)

    def cancel(self):
        """"""
        self.main.worker.cancelled = True
        #self.main.infobox.setText('Operation Canceled')
        QObject.deleteLater(self.main.worker)
        self.main.thread.quit()
        self.main.led_control.turn_off()
        #self.main.change_operation(self.main.idle_op)

    def finished(self):
        #self.ui.infobox.setText('Operation Finished')
        #self.main.thread.quit()
        self.main.testCanceled()
        '''self.ui.change_operation(self.ui.idle_op)'''


class LEDWorker(QObject):
    """  """
    wavelength = pyqtSignal(str)
    finished = pyqtSignal()
    cancelled = False

    main = None

    def cycle_wavelengths(self):

        #Only cycle through the wavelengths that are visible
        for wavelength in self.main.led_control.wavelength_list[4:12]:
            self.main.led_control.turn_on(wavelength)
            self.wavelength.emit(wavelength)
            i = 0
            while (i <= 1):
                if self.cancelled:
                    self.main.led_control.turn_off()
                    return 0
                time.sleep(0.1)
                i = i + 0.1
            self.main.led_control.turn_off()
            
        self.finished.emit()

'''
def click_TestLEDs(window, led_control):
    print(window)
    window.FocusButton.setEnabled(False)
    window.CaptureButton.setEnabled(False)
    window.FlatsButton.setEnabled(False)
    window.CancelButton.setEnabled(True)
    window.infobox.setText("Testing LEDs")
    cycle_wavelengths(window, led_control)

if __name__ == '__main__':
    cycle_wavelengths(None)
'''