import sys, os
from PyQt5 import uic, QtWidgets
from operations.led_control import LEDController
from operations.led_test_mode import click_TestLEDs

class Ui(QtWidgets.QMainWindow):
    led_control = LEDController()

    def __init__(self, parent=None):
        
        if getattr(sys, 'frozen', False):
            RELATIVE_PATH = os.path.dirname(sys.executable)
        else:
            RELATIVE_PATH = os.path.dirname(__file__)

        super(Ui, self).__init__(parent)
        self._ui_path = RELATIVE_PATH + "/skeleton"  
        uic.loadUi(os.path.join(self._ui_path, 'capture-mode2.ui'), self)
        self.connect_buttons()

    def focus_mode_start(self):
        self.CaptureButton.setEnabled(False)
        self.TestLedsButton.setEnabled(False)
        self.FlatsButton.setEnabled(False)
        self.LightLevelsButton.setEnabled(False)
        self.CancelButton.setEnabled(True)
        self.led_control.turn_on(self.led_control.wavelength_list[11]) #630 nm (red)

    def cancel(self):
        #Enable Capture, Flats, and Light Levels once we start them
        self.infobox.setText('Operation Canceled')
        self.FocusButton.setEnabled(True)
        #self.CaptureButton.setEnabled(True)
        self.TestLedsButton.setEnabled(True)
        #self.FlatsButton.setEnabled(True)
        #self.LightLevelsButton.setEnabled(True)
        self.CancelButton.setEnabled(False)
        self.led_control.turn_off()

    def connect_buttons(self):
        self.CancelButton.clicked.connect(self.cancel)
        self.FocusButton.clicked.connect(self.focus_mode_start)
        #TODO!! Add QThread here so TestLEDs doesn't block the GUI
        self.TestLedsButton.clicked.connect(lambda: click_TestLEDs(window, self.led_control))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())