from operations.operation import Operation

class IdleMode(Operation):
    """
    """
    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(True)
        self.ui.TestLedsButton.setEnabled(True)
        self.ui.FlatsButton.setEnabled(True)
        self.ui.LightLevelsButton.setEnabled(True)
        self.ui.FocusButton.setEnabled(True)
        self.ui.CancelButton.setEnabled(False)
        self.ui.LargeDisplay.clear()

    def cancel(self):
        """"""
        pass

    def finished(self):
        pass
