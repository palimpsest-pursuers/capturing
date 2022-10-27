#import sys, os, abc
#from PyQt5 import uic, QtWidgets
#from operations.led_control import LEDController
#from operations.led_test_mode import click_TestLEDs
#from operation_interface import OperationInterface
from operations.operation import Operation
#from idle_mode import IdleMode

class FocusMode(Operation):
    """
    """
    ui = None

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11]) #630 nm (red)

    def cancel(self):
        """"""
        #Enable Capture, Flats, and Light Levels once we start them
        self.ui.infobox.setText('Operation Canceled')
        #self.FocusButton.setEnabled(True)
        #self.CaptureButton.setEnabled(True)
        #self.TestLedsButton.setEnabled(True)
        #self.FlatsButton.setEnabled(True)
        #self.LightLevelsButton.setEnabled(True)
        #self.CancelButton.setEnabled(False)
        self.ui.led_control.turn_off()
        self.ui.change_operation(self.ui.idle_op)

    def set_infobox(self):
        """  """
        self.ui.infobox.setText("FOCUSED!")

    def big_display():
        """  """
        pass
    
    def small_top_display(self):
        """  """
        pass

    def small_middle_display(self):
        """  """
        pass