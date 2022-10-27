import sys, os
from PyQt5 import uic, QtWidgets
from operations.led_control import LEDController
from operations.led_test_mode import click_TestLEDs
from operations.operation import Operation


class Ui(QtWidgets.QMainWindow):
    led_control = LEDController()
    focus_op = None
    idle_op = None
    _current_op = None

    def __init__(self, parent=None):
        
        if getattr(sys, 'frozen', False):
            RELATIVE_PATH = os.path.dirname(sys.executable)
        else:
            RELATIVE_PATH = os.path.dirname(__file__)

        super(Ui, self).__init__(parent)
        self._ui_path = RELATIVE_PATH + "/skeleton"  
        uic.loadUi(os.path.join(self._ui_path, 'capture-mode2.ui'), self)

        from operations.focus_mode import FocusMode
        self.focus_op = FocusMode()
        self.focus_op.set_ui(self)
        from operations.idle_mode import IdleMode
        self.idle_op = IdleMode()
        self.idle_op.set_ui(self)

        self.change_operation(self.idle_op)
        self.connect_buttons()

    def connect_buttons(self):
        self.CancelButton.clicked.connect(lambda: self.cancel_op())
        self.FocusButton.clicked.connect(lambda: self.change_operation(self.focus_op))
        #TODO!! Add QThread here so TestLEDs doesn't block the GUI
        self.TestLedsButton.clicked.connect(lambda: click_TestLEDs(window, self.led_control))

    def change_operation(self, op: Operation):
        """   """
        print("operation has been changed")
        self._current_op = op
        self._current_op.ui = self
        self._current_op.on_start()
        #self._currentOp.

    def cancel_op(self):
        print("operation has been canceled")
        self._current_op.cancel()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())