import sys, os
from PyQt5 import uic, QtWidgets, QtCore
import numpy as np
from controllers.camera_mock import CameraMock
from controllers.led_mock import LEDMock
from controllers.pixilink_controller import PixilinkController
from controllers.blackfly_controller import BlackflyController
from controllers.led_controller import LEDController
from operations.operation import Operation
from cube_creation.build_cube import CubeBuilder

class Ui(QtWidgets.QMainWindow):
    led_control = LEDMock()  
    camera_control = None
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

        try:
            self.camera_control = PixilinkController()
            self.pixilinkSelect.setChecked(True)
        except:
            self.intro_text += '\nPixilink camera initialization failed, ensure wired connection to computer and try again.\n'
            self.camera_control = BlackflyController()
            self.lightStartButton.setDisabled(True)
            self.blackflySelect.setChecked(True)

        try:
            self.led_control = LEDController()
        except:
            self.intro_text += '\nLED panel initialization failed, ensure wired connection to computer and select LED version to try again.\n'
            self.led_control = LEDMock()

        self.startingInfo.setText(self.intro_text)
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
        self.LEDversion1.clicked.connect(lambda: self.LEDv1Selected())
        self.LEDversion2.clicked.connect(lambda: self.LEDv2Selected())
        self.blackflySelect.clicked.connect(lambda: self.blackflySelected())
        self.pixilinkSelect.clicked.connect(lambda: self.pixilinkSelected())
        self.LEDversion2.setChecked(True)

    def LEDv1Selected(self):
        if type(self.led_control) == type(LEDMock()):
            try:
                self.led_control = LEDController()
            except:
                self.intro_text += '\nLED panel initialization failed, ensure wired connection to computer and select LED version to try again.\n'
               
        self.startingInfo.setText(self.intro_text)

        self.led_control.wavelength_list = ['365','385','395','420',
                                            '450','470','490','520',
                                            '560','590','615','630',
                                            '660','730','850','940']

    def LEDv2Selected(self):
        if type(self.led_control) == type(LEDMock()):
            try:
                self.led_control = LEDController()
            except:
                self.intro_text += '\nLED panel initialization failed, ensure wired connection to computer and select LED version to try again.\n'

        self.startingInfo.setText(self.intro_text)

        self.led_control.wavelength_list = ['365', '385', '395', '420',
                                            '450', '470', '500', '530', 
                                            '560', '590', '615', '630', 
                                            '660', '730', '850', '940']
        
    def pixilinkSelected(self):
        try:
            self.camera_control = PixilinkController()
            self.lightStartButton.setDisabled(False)
        except:
            self.startingInfo.setText(self.intro_text + 
                                        '\nPixilink camera initialization failed, ensure wired connection to computer and try again.\n')

    def blackflySelected(self):
        self.camera_control = BlackflyController()
        self.lightStartButton.setDisabled(True)

    def connectMetadataButtons(self):
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
            self.titleLabel.setStyleSheet('color:rgb(0, 0, 0);')
            self.institutionOrOwnerLabel.setStyleSheet('color:rgb(0, 0, 0);')
            self.dateLabel.setStyleSheet('color:rgb(0, 0, 0);')
            self.setPageWithinPage(self.capturingOps, self.noiseOp, self.noiseSteps, self.noiseStep0)

    def connectNoiseButtons(self):
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
        self.objectCancel0Button.clicked.connect(lambda: self.cancelClicked())
        self.objectStartButton.clicked.connect(lambda: self.objectStart())
        self.objectCancel1Button.clicked.connect(lambda: self.cancelOp(self.objectSteps, self.objectStep0, self.object_op))
        self.objectRedoButton.clicked.connect(lambda: self.objectStart())
        self.objectCancel2Button.clicked.connect(lambda: self.cancelOpClicked(self.object_op))
        self.objectContinueButton.clicked.connect(lambda: self.objectContinue())
        self.objectRedo2Button.clicked.connect(lambda: self.objectStart())
        self.objectComboBox.addItems(self.led_control.wavelength_list)
        self.objectComboBox.currentIndexChanged.connect(lambda: self.objectDisplay(self.objectComboBox.currentIndex()))
        

    def objectStart(self):
        #print("DO THE THING  - object img")
        self.object_op.on_start()
        self.setPage(self.objectSteps, self.objectStep1)
        
    def objectDisplay(self, i):
        frame = self.cube_builder.img_array[:,:,i]
        img = self.camera_control.convert_nparray_to_QPixmap(frame)
        scene = QtWidgets.QGraphicsScene()
        self.objectStep2View.setScene(scene)
        self.objectStep2View.setHidden(False)
        scene.addPixmap(img.scaled(self.objectStep2View.width(), self.objectStep2View.height(), QtCore.Qt.KeepAspectRatio))

        '''x = self.cube_builder.img_array.shape[0]
        y = self.cube_builder.img_array.shape[1]
        xstart = x/3
        xend = xstart*2
        ystart = y/3
        yend = ystart*2
        zoom = self.cube_builder.img_array[xstart:xend,ystart:yend, i]
        zoomImg = self.camera_control.convert_nparray_to_QPixmap(zoom)
        zscene = QtWidgets.QGraphicsScene()
        self.objectStep2Zoom.setScene(zscene)
        self.objectStep2Zoom.setHidden(False)
        zscene.addPixmap(zoomImg.scaled(self.objectStep2Zoom.width(), zoomImg.objectStep2Zoom.height(), QtCore.Qt.KeepAspectRatio))

        hist = histogram, bins = np.histogram(frame, bins=20, range=(0, 255))  # use 20 bins and a range of 0-255
        hscene = QtWidgets.QGraphicsScene()

        # Determine the width and height of the scene
        width = self.main.objectStep2Hist.width() - 14
        height =  self.main.objectStep2Hist.height() - 14

        # Create a QGraphicsRectItem object for each histogram bar
        bar_width = width / len(hist)
        max_height = max(hist)
        for i, value in enumerate(hist):
            bar_height = height * value / max_height
            bar = QtWidgets.QGraphicsRectItem(i * bar_width, height - bar_height, bar_width, bar_height)
            hscene.addItem(bar)

        self.main.objectStep2Hist.setScene(hscene)'''

    def objectContinue(self):
        #print("SAVE THE THING - object images")
        self.object_op.finished()
        self.setPageWithinPage(self.capturingOps, self.flatsOp, self.flatsSteps, self.flatsStep0)

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

    def flatsDisplay(self, i):
        try:
            frame = self.cube_builder.flats_array[:,:,i]
            img = self.camera_control.convert_nparray_to_QPixmap(frame)
            scene = QtWidgets.QGraphicsScene()
            self.flatsStep2View.setScene(scene)
            self.flatsStep2View.setHidden(False)
            scene.addPixmap(img.scaled(self.flatsStep2View.width(), self.flatsStep2View.height(), QtCore.Qt.KeepAspectRatio))

            '''x = self.cube_builder.flats_array.shape[0]
            y = self.cube_builder.flats_array.shape[1]
            xstart = x/3
            xend = xstart*2
            ystart = y/3
            yend = ystart*2
            zoom = self.cube_builder.flats_array[xstart:xend,ystart:yend, i]
            zoomImg = self.camera_control.convert_nparray_to_QPixmap(zoom)
            zscene = QtWidgets.QGraphicsScene()
            self.flatsStep2Zoom.setScene(zscene)
            self.flatsStep2Zoom.setHidden(False)
            zscene.addPixmap(zoomImg.scaled(self.flatsStep2Zoom.width(), zoomImg.flatsStep2Zoom.height(), QtCore.Qt.KeepAspectRatio))

            hist = histogram, bins = np.histogram(frame, bins=20, range=(0, 255))  # use 20 bins and a range of 0-255
            hscene = QtWidgets.QGraphicsScene()

            # Determine the width and height of the scene
            width = self.main.flatsStep2Hist.width() - 14
            height =  self.main.flatsStep2Hist.height() - 14

            # Create a QGraphicsRectItem object for each histogram bar
            bar_width = width / len(hist)
            max_height = max(hist)
            for i, value in enumerate(hist):
                bar_height = height * value / max_height
                bar = QtWidgets.QGraphicsRectItem(i * bar_width, height - bar_height, bar_width, bar_height)
                hscene.addItem(bar)

            self.main.flatsStep2Hist.setScene(hscene)'''
        except:
            pass

    def flatsContinue(self):
        #print("SAVE THE THING - flats")
        self.flats_op.finished()
        self.edit_op.on_start()
        self.setPage(self.capturingOps, self.editOp)

    def connectEditButtons(self):
        self.editCancelButton.clicked.connect(lambda: self.cancelOpClicked(self.edit_op))
        self.editContinueButton.clicked.connect(lambda: self.editContinue())
        self.editSkipButton.clicked.connect(lambda: self.editContinue())
        self.rotateButton.clicked.connect(lambda: self.rotate())
        self.cropButton.clicked.connect(lambda: self.crop())
        self.cropCancelButton.clicked.connect(lambda: self.cropCancel())
        self.autoButton.clicked.connect(lambda: self.autoCalibrate())
        self.calibrationButton.clicked.connect(lambda: self.calibrate())
        #self.calibrationCancel.clicked.connect(lambda: self.calibrateCancel())

    def rotate(self):
        self.edit_op.rotate()

    def crop(self):
        self.edit_op.crop()

    def cropCancel(self):
        pass

    def autoCalibrate(self):
        self.edit_op.auto_calibrate()

    def calibrate(self):
        self.edit_op.calibrate()

    def calibrateCancel(self):
        pass
    
    def editContinue(self):
        #print("SAVE THE THING - edit")
        self.edit_op.finished()
        self.setPage(self.capturingOps, self.finishOp)
        self.finishDisplay(0)

    def connectFinishButtons(self):
        self.finishCancelButton.clicked.connect(lambda: self.cancelOpClicked(self.finish_op))
        self.finishFinishButton.clicked.connect(lambda: self.finishFinish())
        self.finishRedoButton.clicked.connect(lambda: self.finishRedo())
        self.finishComboBox.addItems(self.led_control.wavelength_list)
        self.finishComboBox.currentIndexChanged.connect(lambda: self.finishDisplay(self.finishComboBox.currentIndex()))

    def finishDisplay(self, i):
        frame = self.cube_builder.final_array[:,:,i]
        img = self.camera_control.convert_nparray_to_QPixmap(frame)
        scene = QtWidgets.QGraphicsScene()
        self.finishView.setScene(scene)
        self.finishView.setHidden(False)
        scene.addPixmap(img.scaled(self.finishView.width(), self.finishView.height(), QtCore.Qt.KeepAspectRatio))

    def finishFinish(self):
        self.finish_op.on_start()
        

    def finishRedo(self):
        print("REDO THE ENTIRE THING")
        self.finish_op.cancel()
        self.setPageWithinPage(self.capturingOps, self.noiseOp, self.noiseSteps, self.noiseStep0)
    
    def finishDone(self):
        self.setPage(self.pages, self.startingPage)

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
        try:
            self.testLEDsButton.setText("Cancel Test LEDs")
            self.testLEDsButton.clicked.connect(lambda: self.testCanceled())
            self.led_op.on_start(self)
        except:
            self.startingInfo.setText("Error in test LEDs clicked")
    
    def testCanceled(self):
        try:
            self.led_op.cancel()
            self.testLEDsButton.clicked.connect(lambda: self.testLEDsClicked())
            self.testLEDsButton.setText("Test LEDs")
        except:
            self.startingInfo.setText("Error in test LEDs cancel")
        #self.startingInfo.setText(self.intro_text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())