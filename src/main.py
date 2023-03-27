import sys, os
from PyQt5 import uic, QtWidgets
from controllers.camera_mock import CameraMock
from controllers.led_mock import LEDMock
from controllers.pixilink_controller import PixilinkController
from controllers.blackfly_controller import BlackflyController
#from controllers.led_controller import LEDController
from operations.operation import Operation
from dialogs.metadata_entry import MetadataEntryDialog
from datetime import date



class Ui(QtWidgets.QMainWindow):
    led_control = LEDMock() #()
    camera_control =  BlackflyController()
    idle_op = None
    capture_op = None
    flat_op = None
    focus_op = None
    level_op = None
    testled_op = None
    _current_op = None
    metadata = None

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
        self.TopRightLabel.setVisible(False)
        self.TestLedsButton.clicked.connect(lambda: self.change_operation(self.testled_op))
        self.LightDisplayTL.setEnabled(False)
        self.LightDisplayTR.setEnabled(False)
        self.LightDisplayBL.setEnabled(False)
        self.LightDisplayBR.setEnabled(False)
        self.LightDisplayTL.setVisible(False)
        self.LightDisplayTR.setVisible(False)
        self.LightDisplayBL.setVisible(False)
        self.LightDisplayBR.setVisible(False)

    def connect_buttons(self):
        """Connects the UI buttons to their corresponding operation"""
        self.CancelButton.clicked.connect(lambda: self.cancel_op())
        self.CaptureButton.clicked.connect(lambda: self.wrapped_show_metadata_dialog(self.capture_op))
        self.FlatsButton.clicked.connect(lambda: self.change_operation(self.flat_op))
        self.FocusButton.clicked.connect(lambda: self.change_operation(self.focus_op))
        self.LightLevelsButton.clicked.connect(lambda: self.change_operation(self.level_op))
        #TODO!! Add QThread here so TestLEDs doesn't block the GUI
        self.TestLedsButton.clicked.connect(lambda: self.change_operation(self.testled_op))
        self.LightDisplayTL.clicked.connect(lambda: self.level_op.save_level(self.level_op.exposure1))
        self.LightDisplayTR.clicked.connect(lambda: self.level_op.save_level(self.level_op.exposure2))
        self.LightDisplayBL.clicked.connect(lambda: self.level_op.save_level(self.level_op.exposure3))
        self.LightDisplayBR.clicked.connect(lambda: self.level_op.save_level(self.level_op.exposure4))


    def change_operation(self, op: Operation, metadata=None):
        """Changes the state of the system to Operation op"""
        print("operation has been changed")
        self._current_op = op
        self._current_op.ui = self
        self._current_op.on_start()

    def cancel_op(self):
        """Cancels the current operation"""
        print("operation has been canceled")
        self._current_op.cancel()


    def wrapped_change_mode(self, operation):
        metadata = {
            "title": self.subdialog.titleInput.text(),
            "institutionOrOwner": self.subdialog.institutionOrOwnerInput.text(),
            "date": self.subdialog.dateInput.text(),
            "identifyingNumber": self.subdialog.identifyingNumberInput.text(),
            "catalogNumber": self.subdialog.catalogNumberInput.text(),
            "artist": self.subdialog.artistInput.text(),
            "creationDate": self.subdialog.creationDateInput.text(),
            "creditLine": self.subdialog.creditLineInput.text(),
            "material": self.subdialog.materialInput.text(),
            "measurementLengthCM": self.subdialog.measurementLInput.text(),
            "measurementWidthCM": self.subdialog.measurementWInput.text(),
            "operator": self.subdialog.operatorInput.text(),
            "url": self.subdialog.urlInput.text(),
        }
        
        from operations.capture_mode import CaptureMode
        captureOp = CaptureMode()
        self._current_op = captureOp
        self._current_op.ui = self
        self.metadata = metadata
        self._current_op.on_start(metadata=metadata)
        # self.change_operation(operation, metadata=metadata)

    def clear_metadata(self):
        self.subdialog.titleInput.setText("")
        self.subdialog.institutionOrOwnerInput.setText("")
        self.subdialog.identifyingNumberInput.setText("")
        self.subdialog.catalogNumberInput.setText("")
        self.subdialog.artistInput.setText("")
        self.subdialog.creationDateInput.setText("")
        self.subdialog.creditLineInput.setText("")
        self.subdialog.materialInput.setText("")
        self.subdialog.measurementLInput.setText("")
        self.subdialog.measurementWInput.setText("")
        self.subdialog.operatorInput.setText("")
        self.subdialog.urlInput.setText("")

    def wrapped_show_metadata_dialog(self, operation):
        self.subdialog = MetadataEntryDialog(operation, parent=self)
        self.subdialog.accepted.connect(lambda: self.wrapped_change_mode(operation))
        self.subdialog.clearButton.clicked.connect(lambda: self.clear_metadata())
        
        if self.metadata != None:
            self.subdialog.titleInput.setText(self.metadata["title"])
            self.subdialog.institutionOrOwnerInput.setText(self.metadata["institutionOrOwner"])
            self.subdialog.dateInput.setText(self.metadata["date"])
            self.subdialog.identifyingNumberInput.setText(self.metadata["identifyingNumber"])
            self.subdialog.catalogNumberInput.setText(self.metadata["catalogNumber"])
            self.subdialog.artistInput.setText(self.metadata["artist"])
            self.subdialog.creationDateInput.setText(self.metadata["creationDate"])
            self.subdialog.creditLineInput.setText(self.metadata["creditLine"])
            self.subdialog.materialInput.setText(self.metadata["material"])
            self.subdialog.measurementLInput.setText(self.metadata["measurementLengthCM"])
            self.subdialog.measurementWInput.setText(self.metadata["measurementWidthCM"])
            self.subdialog.operatorInput.setText(self.metadata["operator"])
            self.subdialog.urlInput.setText(self.metadata["url"])

        self.subdialog.dateInput.setText(date.today().strftime("%m/%d/%Y"))

        self.subdialog.show()
        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())