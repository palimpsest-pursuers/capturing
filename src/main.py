import sys, os
from PyQt5 import uic, QtWidgets
from operations.camera_control import CameraController
from controllers.led_mock import LEDMock
#from controllers.led_controller import LEDController
from operations.operation import Operation


class Ui(QtWidgets.QMainWindow):
    led_control = LEDMock() #LEDController()
    camera_control = CameraController()
    idle_op = None
    capture_op = None
    flat_op = None
    focus_op = None
    level_op = None
    testled_op = None
    _current_op = None

    def __init__(self, parent=None):
        """Initializes the application"""
        if getattr(sys, 'frozen', False):
            RELATIVE_PATH = os.path.dirname(sys.executable)
        else:
            RELATIVE_PATH = os.path.dirname(__file__)

        super(Ui, self).__init__(parent)
        self._ui_path = RELATIVE_PATH + "/skeleton"  
        uic.loadUi(os.path.join(self._ui_path, 'capture-mode2.ui'), self)

        from operations.idle_mode import IdleMode
        self.idle_op = IdleMode()
        self.idle_op.set_ui(self)
        from operations.capture_mode import CaptureMode
        self.capture_op = CaptureMode()
        self.capture_op.set_ui(self)
        from operations.flats_mode import FlatsMode
        self.flat_op = FlatsMode()
        self.flat_op.set_ui(self)
        from operations.focus_mode import FocusMode
        self.focus_op = FocusMode()
        self.focus_op.set_ui(self)
        from operations.light_level_mode import LightLevelMode
        self.level_op = LightLevelMode()
        self.level_op.set_ui(self)
        from operations.led_test_mode import TestLEDMode
        self.testled_op = TestLEDMode()
        self.testled_op.set_ui(self)


        self.change_operation(self.idle_op)
        self.connect_buttons()

    def connect_buttons(self):
        """Connects the UI buttons to their corresponding operation"""
        self.CancelButton.clicked.connect(lambda: self.cancel_op())
        self.CaptureButton.clicked.connect(lambda: self.change_operation(self.capture_op))
        self.FlatsButton.clicked.connect(lambda: self.change_operation(self.flat_op))
        self.FocusButton.clicked.connect(lambda: self.change_operation(self.focus_op))
        self.LightLevelsButton.clicked.connect(lambda: self.change_operation(self.level_op))
        #TODO!! Add QThread here so TestLEDs doesn't block the GUI
        self.TestLedsButton.clicked.connect(lambda: self.change_operation(self.testled_op))

    def change_operation(self, op: Operation):
        """Changes the state of the system to Operation op"""
        print("operation has been changed")
        self._current_op = op
        self._current_op.ui = self
        self._current_op.on_start()

    def cancel_op(self):
        """Cancels the current operation"""
        print("operation has been canceled")
        self._current_op.cancel()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())