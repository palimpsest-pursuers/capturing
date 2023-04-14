import sys, os
from PyQt5 import uic, QtWidgets, QtCore
from controllers.camera_mock import CameraMock
from controllers.led_mock import LEDMock
from controllers.pixilink_controller import PixilinkController
from controllers.blackfly_controller import BlackflyController
from controllers.led_controller import LEDController
from operations.operation import Operation
from cube_creation.build_cube import CubeBuilder

class Ui(QtWidgets.QMainWindow):
    led_control = LEDController()  
    camera_control = PixilinkController() #BlackflyController() 
    intro_text = 'Welcome to MISHA Image Capturing Software!\n'
    metadata = {}
    noiseImg = None
    led_op = None
    noise_op = None
    focus_op = None
    light_op = None
    object_op = None
    flats_op = None
    edit_op = None
    finish_op = None
    cube_builder = CubeBuilder()


    def __init__(self, parent=None):
        """Initializes the application"""
        if getattr(sys, 'frozen', False):
            RELATIVE_PATH = os.path.dirname(sys.executable)
        else:
            RELATIVE_PATH = os.path.dirname(__file__)

        super(Ui, self).__init__(parent)
        self._ui_path = RELATIVE_PATH + "/skeleton"  
        uic.loadUi(os.path.join(self._ui_path, 'capture.ui'), self)

        self.pages.setCurrentWidget(self.startingPage)
        self.connectButtons()
        self.setOperations()
        self.startingInfo.setText(self.intro_text)
        
    def setOperations(self):
        from operations.led_test_mode import TestLEDMode
        self.led_op = TestLEDMode()
        self.led_op.set_main(self)

        from operations.noise_operation import NoiseOp
        self.noise_op = NoiseOp()
        self.noise_op.set_main(self)

        from operations.focus_operation import FocusOp
        self.focus_op = FocusOp()
        self.focus_op.set_main(self)

        from operations.light_operation import LightOp
        self.light_op = LightOp()
        self.light_op.set_main(self)

        from operations.object_operation import ObjectOp
        self.object_op = ObjectOp()
        self.object_op.set_main(self)

        from operations.flats_operation import FlatsOp
        self.flats_op = FlatsOp()
        self.flats_op.set_main(self)

        from operations.edit_operation import EditOp
        self.edit_op = EditOp()
        self.edit_op.set_main(self)

        from operations.finish_operation import FinishOp
        self.finish_op = FinishOp()
        self.finish_op.set_main(self)

    def connectButtons(self):
        self.connectStartingButtons()
        self.connectMetadataButtons()
        self.connectNoiseButtons()
        self.connectFocusButtons()
        self.connectLightButtons()
        self.connectObjectButtons()
        self.connectFlatsButtons()
        self.connectEditButtons()
        self.connectFinishButtons()

    def connectStartingButtons(self):
        self.testLEDsButton.clicked.connect(lambda: self.testLEDsClicked())
        self.startButton.clicked.connect(lambda: self.setPageWithinPage(self.pages, self.capturingPage,self.capturingOps, self.metadataOp))

    def connectMetadataButtons(self):
        self.metadataMenuButton.clicked.connect(lambda: self.menuClicked(1))
        self.metadataCancelButton.clicked.connect(lambda: self.cancelClicked())
        self.metadataClearButton.clicked.connect(lambda: self.metadataClear())
        self.metadataContinueButton.clicked.connect(lambda: self.metadataContinue())

    def metadataClear(self):
        self.titleInput.setText("")
        self.institutionOrOwnerInput.setText("")
        self.identifyingNumberInput.setText("")
        self.catalogNumberInput.setText("")
        self.artistInput.setText("")
        self.creationDateInput.setText("")
        self.creditLineInput.setText("")
        self.materialInput.setText("")
        self.measurementLInput.setText("")
        self.measurementWInput.setText("")
        self.operatorInput.setText("")
        self.urlInput.setText("")
        self.metadata = None

    def metadataContinue(self):
        self.metadata = {
            "title": self.titleInput.text(),
            "institutionOrOwner": self.institutionOrOwnerInput.text(),
            "date": self.dateInput.text(),
            "identifyingNumber": self.identifyingNumberInput.text(),
            "catalogNumber": self.catalogNumberInput.text(),
            "artist": self.artistInput.text(),
            "creationDate": self.creationDateInput.text(),
            "creditLine": self.creditLineInput.text(),
            "material": self.materialInput.text(),
            "measurementLengthCM": self.measurementLInput.text(),
            "measurementWidthCM": self.measurementWInput.text(),
            "operator": self.operatorInput.text(),
            "url": self.urlInput.text(),
        }
        self.setPageWithinPage(self.capturingOps, self.noiseOp, self.noiseSteps, self.noiseStep0)

    def connectNoiseButtons(self):
        self.noiseMenuButton.clicked.connect(lambda: self.menuClicked(2))
        self.noiseCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.noiseSkipButton.clicked.connect(lambda: self.setPageWithinPage(self.capturingOps, self.focusOp, self.focusSteps, self.focusStep0))
        self.noiseStartButton.clicked.connect(lambda: self.noiseStart())
        self.noiseCancel1Button.clicked.connect(lambda: self.cancelOp(self.noiseSteps,self.noiseStep0, self.noise_op))
        self.noiseContinueButton.clicked.connect(lambda: self.noiseContinue())
        self.noiseRetakeButton.clicked.connect(lambda: self.noiseStart())

    def noiseStart(self):
        #print("DO THE THING - noise")
        self.noise_op.on_start()
        self.setPage(self.noiseSteps, self.noiseStep1)

    def noiseContinue(self):
        #print("SAVE THE THING - noise")
        self.noise_op.finished()
        self.setPageWithinPage(self.capturingOps, self.focusOp, self.focusSteps, self.focusStep0)

    def connectFocusButtons(self):
        self.focusMenuButton.clicked.connect(lambda: self.menuClicked(3))
        self.focusCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.focusSkipButton.clicked.connect(lambda: self.setPageWithinPage(self.capturingOps, self.lightOp, self.lightSteps, self.lightStep0))
        self.focusStartButton.clicked.connect(lambda: self.focusStart())
        self.focusCancel1Button.clicked.connect(lambda: self.cancelOp(self.focusSteps, self.focusStep0, self.focus_op))
        self.focusContinueButton.clicked.connect(lambda: self.focusContinue())

    def focusStart(self):
        #print("DO THE THING - focus")
        self.focus_op.on_start()
        self.setPage(self.focusSteps, self.focusStep1)

    def focusContinue(self):
        #print("STOP THE THING - focus")
        self.focus_op.cancel()
        self.setPageWithinPage(self.capturingOps, self.lightOp, self.lightSteps, self.lightStep0)

    def connectLightButtons(self):
        self.lightMenuButton.clicked.connect(lambda: self.menuClicked(4))
        self.lightCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.lightSkip0Button.clicked.connect(lambda: self.setPageWithinPage(self.capturingOps, self.objectOp, self.objectSteps, self.objectStep0))
        self.lightStartButton.clicked.connect(lambda: self.lightStart())
        self.lightCancel1Button.clicked.connect(lambda: self.cancelOp(self.lightSteps, self.lightStep0, self.light_op))
        self.lightSkip1Button.clicked.connect(lambda: self.setPageWithinPage(self.capturingOps, self.objectOp, self.objectSteps, self.objectStep0))
        self.lightLevel0.clicked.connect(lambda: self.lightLevelSelected(1.0))
        self.lightLevel1.clicked.connect(lambda: self.lightLevelSelected(0.6))
        self.lightLevel2.clicked.connect(lambda: self.lightLevelSelected(1.5))
        self.lightLevel3.clicked.connect(lambda: self.lightLevelSelected(2.0))

    def lightStart(self):
        #print("DO THE THING - light")
        self.light_op.on_start()
        self.setPage(self.lightSteps, self.lightStep1)

    def lightLevelSelected(self, num):
        #print("SAVE THE THING (",num,") - light")
        self.lightLevel0.setEnabled(False)
        self.lightLevel1.setEnabled(False)
        self.lightLevel2.setEnabled(False)
        self.lightLevel3.setEnabled(False)
        self.light_op.finished()
        self.setPageWithinPage(self.capturingOps, self.objectOp, self.objectSteps, self.objectStep0)

    def connectObjectButtons(self):
        self.objectMenuButton.clicked.connect(lambda: self.menuClicked(5))
        self.objectCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.objectStartButton.clicked.connect(lambda: self.objectStart())
        self.objectCancel1Button.clicked.connect(lambda: self.cancelOp(self.objectSteps, self.objectStep0, self.object_op))
        self.objectRedoButton.clicked.connect(lambda: self.objectStart())
        self.objectCancel2Button.clicked.connect(lambda: self.cancelOpClicked(self.object_op))
        self.objectContinueButton.clicked.connect(lambda: self.objectContinue())
        self.objectRedo2Button.clicked.connect(lambda: self.objectStart())

    def objectStart(self):
        #print("DO THE THING  - object img")
        self.object_op.on_start()
        self.setPage(self.objectSteps, self.objectStep1)
        

    def objectContinue(self):
        #print("SAVE THE THING - object images")
        self.object_op.finished()
        self.setPageWithinPage(self.capturingOps, self.flatsOp, self.flatsSteps, self.flatsStep0)

    def connectFlatsButtons(self):
        self.flatsMenuButton.clicked.connect(lambda: self.menuClicked(6))
        self.flatsCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.flatsSkip0Button.clicked.connect(lambda: self.flatsSkip())
        self.flatsStartButton.clicked.connect(lambda: self.flatsStart())
        self.flatsCancel1Button.clicked.connect(lambda: self.cancelOp(self.flatsSteps, self.flatsStep0, self.flats_op))
        self.flatsSkip1Button.clicked.connect(lambda: self.flatsMidSkip())
        self.flatsCancel2Button.clicked.connect(lambda: self.cancelOpClicked(self.flats_op))
        self.flatsContinueButton.clicked.connect(lambda: self.flatsContinue())
        self.flatsRedo2Button.clicked.connect(lambda: self.flatsStart())
        self.flatsSkip2Button.clicked.connect(lambda: self.setPage(self.capturingOps, self.editOp))

    def flatsSkip(self):
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)

    def flatsStart(self):
        #print("DO THE THING - flats")
        self.flats_op.on_start()
        self.setPage(self.flatsSteps, self.flatsStep1)

    def flatsMidSkip(self):
        #print("STOP AND SKIP THE THING - flats")
        self.flats_op.cancel()
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)

    def flatsContinue(self):
        #print("SAVE THE THING - flats")
        self.flats_op.finished()
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)

    def connectEditButtons(self):
        self.editMenuButton.clicked.connect(lambda: self.menuClicked(7))
        self.editCancelButton.clicked.connect(lambda: self.cancelOpClicked(self.edit_op))
        self.editContinueButton.clicked.connect(lambda: self.editContinue())
        self.editSkipButton.clicked.connect(lambda: self.editContinue())
        self.rotateButton.clicked.connect(lambda: self.rotate())
        self.cropButton.clicked.connect(lambda: self.crop())
        self.cropCancel.clicked.connect(lambda: self.cropCancel())
        self.autoButton.clicked.connect(lambda: self.autoCalibrate())
        self.calibrationButton.clicked.connect(lambda: self.calibrate())
        self.calibrationCancel.clicked.connect(lambda: self.calibrateCancel())

    def rotate(self):
        self.edit_op.rotate()

    def crop(self):
        self.edit_op.crop()

    def cropCancel(self):
        pass

    def autoCalibrate(self):
        self.edit_op.auto_calibrate()

    def calibrate(self):
        pass

    def calibrateCancel(self):
        pass
    
    def editContinue(self):
        #print("SAVE THE THING - edit")
        self.edit_op.finished()
        self.setPage(self.capturingOps, self.finishOp)

    def connectFinishButtons(self):
        self.finishMenuButton.clicked.connect(lambda: self.menuClicked(8))
        self.finishCancelButton.clicked.connect(lambda: self.cancelOpClicked(self.finish_op))
        self.finishFinishButton.clicked.connect(lambda: self.finishFinish())
        self.finishRedoButton.clicked.connect(lambda: self.finishRedo())

    def finishFinish(self):
        #print("Done")
        
        self.finish_op.on_start()
        self.setPage(self.pages, self.startingPage)

    def finishRedo(self):
        print("REDO THE ENTIRE THING")
        self.finish_op.cancel()
        self.setPageWithinPage(self.capturingOps, self.noiseOp, self.noiseSteps, self.noiseStep0)

    def setPage(self, widget, page):
        widget.setCurrentWidget(page)

    def setPageWithinPage(self, widget1, page1, widget2, page2):
        widget2.setCurrentWidget(page2)
        widget1.setCurrentWidget(page1)

    def cancelClicked(self):
        print("CANCELED")
        self.setPage(self.pages, self.startingPage)

    def cancelOpClicked(self,  currentOp=Operation):
        print("CANCELED")
        currentOp.cancel()
        self.setPage(self.pages, self.startingPage)

    def cancelOp(self, currentOpSteps, goToStep, currentOp=Operation):
        print("smol cancel")
        currentOp.cancel()
        self.setPage(currentOpSteps, goToStep)

    def menuClicked(self, currentOP):
        pass

    def testLEDsClicked(self):
        self.testLEDsButton.setText("Cancel Test LEDs")
        self.testLEDsButton.clicked.connect(lambda: self.testCanceled())
        self.led_op.on_start()
    
    def testCanceled(self):
        self.led_op.cancel()
        self.testLEDsButton.clicked.connect(lambda: self.testLEDsClicked())
        self.testLEDsButton.setText("Test LEDs")
        #self.startingInfo.setText(self.intro_text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())