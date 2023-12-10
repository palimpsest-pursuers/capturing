from datetime import date
import sys, os
from PyQt5 import uic, QtWidgets, QtCore
from controllers.led_mock import LEDMock
from controllers.pixilink_controller import PixilinkController
from controllers.blackfly_controller import BlackflyController
from controllers.led_controller import LEDController
from operations.operation import Operation
from cube_creation.build_cube import CubeBuilder

'''
MISHA Image Capturing Software Main 
Authors: Cecelia Ahrens, Mallory Bridge, Eric Gao, Robert Maron
Date: May 10, 2023
'''


class Ui(QtWidgets.QMainWindow):
    led_control = LEDMock()
    camera_control = None
    intro_text = 'Welcome to MISHA Image Capture Software\n\n' \
                 'A low-cost, end-to-end multispectral imaging system, ' \
                 'Multispectral Imaging System for Historical Artifacts ' \
                 '(or “MISHA”), was developed by RIT’s Imaging Science ' \
                 'and Museum Studies Programs to be used on small format ' \
                 'historical documents, sheet, and leaf collections that ' \
                 'have overwritten text, faded ink, or other un-readable or ' \
                 'unknown content. The grant PR-268783-20 was funded by the ' \
                 'National Endowment for the Humanities. See our website: https://chipr2022.wordpress.com/ For ' \
                 'more information, contact please David Messinger and Juilee Decker at RIT.\n' \
                 'Version 3 Python, updated by Sai Keshav Sasanapuri\n'
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

    '''Initializes the UI, Camera controller and LED controller and starts connecting buttons and operations'''

    def __init__(self, parent=None):
        """Initializes the application"""
        if getattr(sys, 'frozen', False):
            RELATIVE_PATH = os.path.dirname(sys.executable)
        else:
            RELATIVE_PATH = os.path.dirname(__file__)

        super(Ui, self).__init__(parent)
        self._ui_path = RELATIVE_PATH + "/skeleton"
        uic.loadUi(os.path.join(self._ui_path, 'capture.ui'), self)

        try:
            self.camera_control = PixilinkController()
            self.pixilinkSelect.setChecked(True)
            init_text = self.intro_text + '\nPixelink camera initialization successful\n'
        except:
            try:
                self.camera_control = BlackflyController()
                self.blackflySelect.setChecked(True)
                init_text = self.intro_text + '\nBlackfly camera initialization successful\n'
            except:
                init_text = self.intro_text + '\nNo cameras found, ensure wired connection to computer and try again.\n'

        try:
            self.led_control = LEDController()
        except:
            init_text += '\nLED panel initialization failed, ensure wired connection to computer and select LED ' \
                         'version to try again.\n'
            self.led_control = LEDMock()

        self.startingInfo.setText(init_text)
        self.pages.setCurrentWidget(self.startingPage)
        self.connectButtons()
        self.setOperations()

    '''Initializes all the individual operations.'''

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

    '''Calls all the button connection/initializaton funcutions divided by what page they appear on'''

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

    '''Connects all the buttons for the starting page to their respective function'''

    def connectStartingButtons(self):
        self.testLEDsButton.clicked.connect(lambda: self.testLEDsClicked())
        self.cancelLEDsButton.clicked.connect(lambda: self.testCanceled())
        self.cancelLEDsButton.setEnabled(False)  # Disabled until the testLEDsButton is clicked
        self.startButton.clicked.connect(
            lambda: self.setPageWithinPage(self.pages, self.capturingPage, self.capturingOps, self.metadataOp))
        self.LEDversion1.clicked.connect(lambda: self.LEDv1Selected())
        self.LEDversion2.clicked.connect(lambda: self.LEDv2Selected())
        self.blackflySelect.clicked.connect(lambda: self.blackflySelected())
        self.pixilinkSelect.clicked.connect(lambda: self.pixilinkSelected())
        self.LEDversion2.setChecked(True)  # Default LED panel versions

    '''Sets the LED panel version to version 1'''

    def LEDv1Selected(self):
        if type(self.led_control) == type(LEDMock()):  # If it had previously failed to connect to the LEDs
            try:
                self.led_control = LEDController()
                # Different versions have different LED wavelengths
                self.led_control.wavelength_list = ['365', '385', '395', '420',
                                                    '450', '470', '490', '520',
                                                    '560', '590', '615', '630',
                                                    '660', '730', '850', '940']
            except:
                self.startingInfo.setText(self.intro_text + '\nLED panel initialization failed, ensure wired '
                                                            'connection to computer and select LED version to try '
                                                            'again.\n')

    '''Sets the LED panel version to version 2 (DEFAULT)'''

    def LEDv2Selected(self):
        if type(self.led_control) == type(LEDMock()):  # If it had previously failed to connect to the LEDs
            try:
                self.led_control = LEDController()
                # Different versions have different LED wavelengths
                self.led_control.wavelength_list = ['365', '385', '395', '420',
                                                    '450', '470', '500', '530',
                                                    '560', '590', '615', '630',
                                                    '660', '730', '850', '940']
            except:
                self.startingInfo.setText(self.intro_text + '\nLED panel initialization failed, ensure wired '
                                                            'connection to computer and select LED version to try '
                                                            'again.\n')

    '''Sets the camera control software to the one for the Pixelink and tries to connect to it. (DEFAULT)'''

    def pixilinkSelected(self):
        try:
            self.camera_control = PixilinkController()
            self.lightStartButton.setDisabled(False)
            self.startingInfo.setText(self.intro_text +
                                      '\nPixelink camera initialization successful\n')
        except:
            self.startingInfo.setText(self.intro_text + '\nPixelink camera initialization failed, ensure wired '
                                                        'connection to computer and try again.\n')

    '''Sets the camera control software to the one for the "Blackfly" and tries to connect to it.'''

    def blackflySelected(self):
        try:
            self.camera_control = BlackflyController()
            self.lightStartButton.setDisabled(False)
            self.startingInfo.setText(self.intro_text + '\nBlackfly camera initialization successful\n')
        except:
            self.startingInfo.setText(self.intro_text + '\nBlackfly camera initialization failed, ensure wired '
                                                        'connection to computer and try again.\n')

    '''Connects all the buttons for the metadata page to their respective function and fills in the date'''

    def connectMetadataButtons(self):
        self.metadataCancelButton.clicked.connect(lambda: self.cancelClicked())
        self.metadataClearButton.clicked.connect(lambda: self.metadataClear())
        self.metadataContinueButton.clicked.connect(lambda: self.metadataContinue())
        today = str(date.today())
        self.dateInput.setText(today)
        self.metadata["date"] = today

    '''Clears all previously entered metadata information and refills in the date'''

    def metadataClear(self):
        today = str(date.today())
        self.dateInput.setText(today)
        self.metadata["date"] = today
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
        self.notesInput.setText("")
        self.metadata = None

    '''
    Saves all entered metadata information and moves to the next page
    UNLESS required information has been left out
        THEN changes label for left out info to red text color
    '''

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
            "notes": self.notesInput.text(),
        }
        # Checks required info has been filled out
        if (self.metadata["title"] == '' or
                self.metadata["institutionOrOwner"] == '' or
                self.metadata["date"] == ''):

            if self.metadata["title"] == '':
                self.titleLabel.setStyleSheet('color:rgb(255, 0, 0);')
            else:
                self.titleLabel.setStyleSheet('color:rgb(0, 0, 0);')

            if self.metadata["institutionOrOwner"] == '':
                self.institutionOrOwnerLabel.setStyleSheet('color:rgb(255, 0, 0);')
            else:
                self.institutionOrOwnerLabel.setStyleSheet('color:rgb(0, 0, 0);')

            if self.metadata["date"] == '':
                self.dateLabel.setStyleSheet('color:rgb(255, 0, 0);')
            else:
                self.dateLabel.setStyleSheet('color:rgb(0, 0, 0);')
        else:
            # resets color
            self.titleLabel.setStyleSheet('color:rgb(0, 0, 0);')
            self.institutionOrOwnerLabel.setStyleSheet('color:rgb(0, 0, 0);')
            self.dateLabel.setStyleSheet('color:rgb(0, 0, 0);')
            # moves to initial info step within next page
            self.setPageWithinPage(self.capturingOps, self.noiseOp, self.noiseSteps, self.noiseStep0)

    '''Connects all the buttons for the noise page to their respective function'''

    def connectNoiseButtons(self):
        self.noiseCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.noiseSkipButton.clicked.connect(
            lambda: self.setPageWithinPage(self.capturingOps, self.focusOp, self.focusSteps, self.focusStep0))
        self.noiseStartButton.clicked.connect(lambda: self.noiseStart())
        self.noiseCancel1Button.clicked.connect(lambda: self.cancelOp(self.noiseSteps, self.noiseStep0, self.noise_op))
        self.noiseContinueButton.clicked.connect(lambda: self.noiseContinue())
        self.noiseRetakeButton.clicked.connect(lambda: self.noiseStart())

    '''Starts noise operation and moves to the noise display step within noise page'''

    def noiseStart(self):
        self.cube_builder.noise = []  # clears noise image array
        self.noise_op.on_start()
        self.setPage(self.noiseSteps, self.noiseStep1)

    '''Finishes noise operation and moves to focus operation page, initial infomation step'''

    def noiseContinue(self):
        self.noise_op.finished()
        self.setPageWithinPage(self.capturingOps, self.focusOp, self.focusSteps, self.focusStep0)

    '''Connects all the buttons for the focus page to their respective function'''

    def connectFocusButtons(self):
        self.focusCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.focusSkipButton.clicked.connect(
            lambda: self.setPageWithinPage(self.capturingOps, self.lightOp, self.lightSteps, self.lightStep0))
        self.focusStartButton.clicked.connect(lambda: self.focusStart())
        self.focusCancel1Button.clicked.connect(lambda: self.cancelOp(self.focusSteps, self.focusStep0, self.focus_op))
        self.focusContinueButton.clicked.connect(lambda: self.focusContinue())

    '''Starts focus operation and moves to the focus display step within focus page'''

    def focusStart(self):
        self.focus_op.on_start()
        self.setPage(self.focusSteps, self.focusStep1)

    '''Finishes focus operation and moves to light operation page, initial infomation step'''

    def focusContinue(self):
        self.focus_op.cancel()
        self.setPageWithinPage(self.capturingOps, self.lightOp, self.lightSteps, self.lightStep0)

    '''Connects all the buttons for the light page to their respective function'''

    def connectLightButtons(self):
        self.lightCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.lightSkip0Button.clicked.connect(
            lambda: self.setPageWithinPage(self.capturingOps, self.objectOp, self.objectSteps, self.objectStep0))
        self.lightStartButton.clicked.connect(lambda: self.lightStart())
        self.lightCancel1Button.clicked.connect(lambda: self.cancelOp(self.lightSteps, self.lightStep0, self.light_op))
        self.lightSkip1Button.clicked.connect(
            lambda: self.setPageWithinPage(self.capturingOps, self.objectOp, self.objectSteps, self.objectStep0))
        self.lightLevel0.clicked.connect(lambda: self.lightLevelSelected(1.0))
        self.lightLevel1.clicked.connect(lambda: self.lightLevelSelected(0.6))
        self.lightLevel2.clicked.connect(lambda: self.lightLevelSelected(1.5))
        self.lightLevel3.clicked.connect(lambda: self.lightLevelSelected(2.0))

    '''Starts light operation and moves to the light display step within light page'''

    def lightStart(self):
        self.light_op.on_start()
        self.setPage(self.lightSteps, self.lightStep1)

    '''Saves the selected light level'''

    def lightLevelSelected(self, num):
        self.light_op.save_level(num)
        self.lightLevel0.setEnabled(False)
        self.lightLevel1.setEnabled(False)
        self.lightLevel2.setEnabled(False)
        self.lightLevel3.setEnabled(False)
        self.light_op.finished()
        self.setPageWithinPage(self.capturingOps, self.objectOp, self.objectSteps, self.objectStep0)

    '''Connects all the buttons for the object page to their respective function'''

    def connectObjectButtons(self):
        self.objectCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.objectStartButton.clicked.connect(lambda: self.objectStart())
        self.objectCancel1Button.clicked.connect(
            lambda: self.cancelOp(self.objectSteps, self.objectStep0, self.object_op))
        self.objectRedoButton.clicked.connect(lambda: self.objectStart())
        self.objectCancel2Button.clicked.connect(lambda: self.cancelOpClicked(self.object_op))
        self.objectContinueButton.clicked.connect(lambda: self.objectContinue())
        self.objectRedo2Button.clicked.connect(lambda: self.objectStart())
        self.objectComboBox.addItems(self.led_control.wavelength_list)
        self.objectComboBox.currentIndexChanged.connect(lambda: self.objectDisplay(self.objectComboBox.currentIndex()))

    '''Starts object operation and moves to the object display step within object page'''

    def objectStart(self):
        self.cube_builder.final_array = []
        self.cube_builder.img_array = []
        self.object_op.on_start()
        self.setPage(self.objectSteps, self.objectStep1)

    '''Changes the wavelength image to display in object display'''

    def objectDisplay(self, i):
        self.objectComboBox.setCurrentIndex(i)
        frame = self.cube_builder.final_array[:, :, i]
        img = self.camera_control.convert_nparray_to_QPixmap(frame)
        scene = QtWidgets.QGraphicsScene()
        self.objectStep2View.setScene(scene)
        self.objectStep2View.setHidden(False)
        scene.addPixmap(
            img.scaled(self.objectStep2View.width(), self.objectStep2View.height(), QtCore.Qt.KeepAspectRatio))

    '''Finishes object operation and moves to flats operation page, initial infomation step'''

    def objectContinue(self):
        self.object_op.finished()
        self.setPageWithinPage(self.capturingOps, self.flatsOp, self.flatsSteps, self.flatsStep0)

    '''Connects all the buttons for the flats page to their respective function'''

    def connectFlatsButtons(self):
        self.flatsCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.flatsSkip0Button.clicked.connect(lambda: self.flatsSkip())
        self.flatsStartButton.clicked.connect(lambda: self.flatsStart())
        self.flatsCancel1Button.clicked.connect(lambda: self.cancelOp(self.flatsSteps, self.flatsStep0, self.flats_op))
        self.flatsSkip1Button.clicked.connect(lambda: self.flatsMidSkip())
        self.flatsCancel2Button.clicked.connect(lambda: self.cancelOpClicked(self.flats_op))
        self.flatsContinueButton.clicked.connect(lambda: self.flatsContinue())
        self.flatsRedo2Button.clicked.connect(lambda: self.flatsStart())
        self.flatsSkip2Button.clicked.connect(lambda: self.setPage(self.capturingOps, self.editOp))
        self.flatsComboBox.addItems(self.led_control.wavelength_list)
        self.flatsComboBox.currentIndexChanged.connect(lambda: self.flatsDisplay(self.flatsComboBox.currentIndex()))

    '''Skips the flats operation and sets the edit display'''

    def flatsSkip(self):
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)
        self.editDisplay(0)

    '''Starts flats operation and moves to the flats display step within flats page'''

    def flatsStart(self):
        self.cube_builder.revert_final()
        self.cube_builder.flats_array = []
        self.flats_op.on_start()
        self.setPage(self.flatsSteps, self.flatsStep1)

    '''Cancels the flats operation and skips forward to the edit operation and sets the display'''

    def flatsMidSkip(self):
        self.flats_op.cancel()
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)
        self.editDisplay(0)

    '''Changes the wavelength image to display in flats display'''

    def flatsDisplay(self, i):
        try:
            self.flatsComboBox.setCurrentIndex(i)
            frame = self.cube_builder.final_array[:, :, i]
            img = self.camera_control.convert_nparray_to_QPixmap(frame)
            scene = QtWidgets.QGraphicsScene()
            self.flatsStep2View.setScene(scene)
            self.flatsStep2View.setHidden(False)
            scene.addPixmap(
                img.scaled(self.flatsStep2View.width(), self.flatsStep2View.height(), QtCore.Qt.KeepAspectRatio))
        except:
            pass

    '''Finishes flats operation and moves to edit operation page and sets the inital display for that page'''

    def flatsContinue(self):
        self.flats_op.finished()
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)
        self.editDisplay(0)

    '''Connects all the buttons for the edit page to their respective function'''

    def connectEditButtons(self):
        self.editCancelButton.clicked.connect(lambda: self.cancelOpClicked(self.edit_op))
        self.editContinueButton.clicked.connect(lambda: self.editContinue())
        self.editSkipButton.clicked.connect(lambda: self.editContinue())
        self.rotateButton.clicked.connect(lambda: self.rotate())
        self.cropButton.clicked.connect(lambda: self.crop())
        self.cropCancelButton.clicked.connect(lambda: self.cropCancel())
        self.autoButton.clicked.connect(lambda: self.autoCalibrate())
        self.calibrationButton.clicked.connect(lambda: self.calibrate())
        self.editComboBox.addItems(self.led_control.wavelength_list)
        self.editComboBox.currentIndexChanged.connect(lambda: self.editDisplay(self.editComboBox.currentIndex()))

    '''Changes the wavelength image to display in edit display'''

    def editDisplay(self, i):
        self.editComboBox.setCurrentIndex(i)
        frame = self.cube_builder.final_array[:, :, i]
        img = self.camera_control.convert_nparray_to_QPixmap(frame)
        self.edit_op.updateEditView(img)

    '''Calls the edit rotate function'''

    def rotate(self):
        self.edit_op.rotate()

    '''Calls the edit crop function'''

    def crop(self):
        self.edit_op.crop()

    def cropCancel(self):
        pass

    '''Calls the edit auto calibration function and disables the calibration buttons'''

    def autoCalibrate(self):
        self.edit_op.auto_calibrate()
        self.autoButton.setEnabled(False)
        self.calibrationButton.setEnabled(False)

    '''Calls the edit calibration functon and disables the auto calibration button'''

    def calibrate(self):
        self.edit_op.calibrate()
        self.autoButton.setEnabled(False)

    '''cancels calibration'''

    def calibrateCancel(self):
        self.autoButton.setEnabled(True)

    '''Finishes edit operation and moves to final operation page and sets the inital display for that page'''

    def editContinue(self):
        self.edit_op.finished()
        self.setPage(self.capturingOps, self.finishOp)
        self.finishDisplay(0)

    '''Connects all the buttons for the finish page to their respective function'''

    def connectFinishButtons(self):
        self.finishCancelButton.clicked.connect(lambda: self.cancelOpClicked(self.finish_op))
        self.finishFinishButton.clicked.connect(lambda: self.finishFinish())
        self.finishRedoButton.clicked.connect(lambda: self.finishRedo())
        self.finishComboBox.addItems(self.led_control.wavelength_list)
        self.finishComboBox.currentIndexChanged.connect(lambda: self.finishDisplay(self.finishComboBox.currentIndex()))

    '''Changes the wavelength image to display in finish display'''

    def finishDisplay(self, i):
        self.finishComboBox.setCurrentIndex(i)
        frame = self.cube_builder.final_array[:, :, i]
        img = self.camera_control.convert_nparray_to_QPixmap(frame)
        scene = QtWidgets.QGraphicsScene()
        self.finishView.setScene(scene)
        self.finishView.setHidden(False)
        scene.addPixmap(img.scaled(self.finishView.width(), self.finishView.height(), QtCore.Qt.KeepAspectRatio))

    '''Finishes and saves everything'''

    def finishFinish(self):
        self.finish_op.on_start()

    '''Redo imaging session without changing the metadata'''

    def finishRedo(self):
        self.finish_op.cancel()
        self.setPageWithinPage(self.capturingOps, self.noiseOp, self.noiseSteps, self.noiseStep0)
        self.autoButton.setEnabled(True)
        self.calibrationButton.setEnabled(True)

    '''Sends the UI back to the start'''

    def finishDone(self):
        self.setPage(self.pages, self.startingPage)
        self.autoButton.setEnabled(True)
        self.calibrationButton.setEnabled(True)

    '''Sets the UI to the given page within the given widget'''

    def setPage(self, widget, page):
        widget.setCurrentWidget(page)

    '''Sets the UI to the given nested pages and widgets'''

    def setPageWithinPage(self, widget1, page1, widget2, page2):
        widget2.setCurrentWidget(page2)
        widget1.setCurrentWidget(page1)

    '''Cancels the entire imaging session and sends the user back to the starting page'''

    def cancelClicked(self):
        self.setPage(self.pages, self.startingPage)
        self.autoButton.setEnabled(True)
        self.calibrationButton.setEnabled(True)

    '''Cancels the entire imaging session and sends the user back to the starting page'''

    def cancelOpClicked(self, currentOp=Operation):
        currentOp.cancel()
        self.setPage(self.pages, self.startingPage)
        self.cube_builder.final_array = []
        self.cube_builder.flats_array = []
        self.cube_builder.img_array = []
        self.cube_builder.noise = []
        self.autoButton.setEnabled(True)
        self.calibrationButton.setEnabled(True)

    '''Cancels a operation and sends the user back to the inital info step for that operation'''

    def cancelOp(self, currentOpSteps, goToStep, currentOp=Operation):
        currentOp.cancel()
        self.setPage(currentOpSteps, goToStep)

    '''Starts the test LED process'''

    def testLEDsClicked(self):
        try:
            self.testLEDsButton.setEnabled(False)
            self.cancelLEDsButton.setEnabled(True)
            self.led_op.on_start(self)
        except:
            self.startingInfo.setText("Error in test LEDs clicked")

    '''Cancels the test LED process'''

    def testCanceled(self):
        try:
            self.cancelLEDsButton.setEnabled(False)
            self.testLEDsButton.setEnabled(True)
            self.led_op.cancel()
            self.startingInfo.setText(self.intro_text)
        except:
            self.startingInfo.setText("Error in test LEDs cancel")

    '''Destructor of the class. Un-Initialize camera and led '''
    def __del__(self):
        print("came here")
        if type(self.led_control) != type(LEDMock()):
            self.led_control.turn_off()
        if self.camera_control is not None:
            self.camera_control.uninitialize_camera()


'''Starts up the Application'''
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
