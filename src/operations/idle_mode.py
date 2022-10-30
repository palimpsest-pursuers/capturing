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

    def cancel(self):
        """"""
        pass
        

    def set_infobox(self):
        """  """
        self.ui.infobox.setText("IDLE!")

    def big_display():
        """  """
        pass
    
    def small_top_display(self):
        """  """
        pass

    def small_middle_display(self):
        """  """
        pass