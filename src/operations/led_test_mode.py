from itertools import cycle
import time
from threading import Thread
from operations.operation import Operation
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt, pyqtSlot

class TestLEDMode(Operation):
    """
    """
    ui = None
    cancelled = False

    def on_start(self):
        """  """
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.ui.thread = QThread()
        self.ui.worker = LEDWorker()
        self.ui.worker.ui = self.ui
        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.thread.started.connect(self.ui.worker.cycle_wavelengths)
        self.ui.worker.wavelength.connect(self.update_text)
        self.ui.infobox.setText("Testing LEDs")
        self.ui.TopRightLabel.setVisible(False)
        #thread = Thread(target=self.cycle_wavelengths())
        #thread.run()
        #self.cycle_wavelengths()
        self.ui.thread.start()

    def update_text(self, text):
        self.ui.infobox.setText(text)

    def cancel(self):
        """"""
        self.ui.worker.cancelled = True
        self.ui.infobox.setText('Operation Canceled')
        self.ui.thread.quit()
        self.ui.led_control.turn_off()
        self.ui.change_operation(self.ui.idle_op)

    '''def finished(self):
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)'''


class LEDWorker(QObject):
    """  """
    wavelength = pyqtSignal(str)
    cancelled = False

    ui = None

    def cycle_wavelengths(self):

        #Only cycle through the wavelengths that are visible
        for wavelength in self.ui.led_control.wavelength_list[4:12]:
            self.ui.led_control.turn_on(wavelength)
            self.wavelength.emit(wavelength)
            i = 0
            while (i <= 1):
                if self.cancelled:
                    self.ui.led_control.turn_off()
                    return 0
                time.sleep(0.1)
                i = i + 0.1
            self.ui.led_control.turn_off()
            
        self.ui._current_op.finished()

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