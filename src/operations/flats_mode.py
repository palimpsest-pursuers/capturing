from operations.operation import Operation

class FlatsMode(Operation):
    """
    """
    ui = None

    def on_start(self):
        """  """
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.set_infobox()
        #self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11]) #630 nm (red)

    def cancel(self):
        """  """
        self.ui.infobox.setText('Operation Canceled')
        self.ui.led_control.turn_off()
        self.ui.change_operation(self.ui.idle_op)

    '''def finished(self):
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)'''