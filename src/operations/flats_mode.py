from operations.capture_mode import *
from PyQt5.QtWidgets import QFileDialog


class FlatsMode(CaptureMode):
    """
    """
    ui = None
    text = "Capturing Flats"

    def on_start(self):
        """  """
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.ui.TopRightLabel.setVisible(True)
        self.ui.LargeDisplay.setVisible(True)
        self.ui.middleRightDisplay.setVisible(True)
        self.ui.infobox.clear()
        self.ui.infobox.setText(self.text)

        self.ui.thread = QThread()
        self.ui.worker = CaptureWorker()
        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.worker.ui = self.ui

        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.sharedFrame.connect(self.updateFrame)
        self.ui.worker.zoomedFrame.connect(self.updateZoomed)
        self.ui.worker.wavelength.connect(self.updateWavelength)



        self.ui.thread.start()

    '''def cancel(self):
        """  """
        self.ui.infobox.setText('Operation Canceled')
        self.ui.led_control.turn_off()
        self.ui.TopRightLabel.setVisible(False)
        self.ui.change_operation(self.ui.idle_op)'''

    '''def finished(self):
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)'''