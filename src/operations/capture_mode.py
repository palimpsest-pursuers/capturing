from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class CaptureMode(Operation):
    """
    """
    ui = None

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(True)
        self.set_infobox()
        image = self.ui.camera_control.camera.run()
        self.ui.LargeDisplay.setPixmap(QPixmap.fromImage(image))
        #self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11]) #630 nm (red)

    def cancel(self):
        """"""
        self.ui.infobox.setText('Operation Canceled')
        self.ui.led_control.turn_off()
        self.ui.change_operation(self.ui.idle_op)

    def set_infobox(self):
        """  """
        self.ui.infobox.setText("CAPTURE!")

    def big_display():
        """  """
        pass
    
    def small_top_display(self):
        """  """
        pass

    def small_middle_display(self):
        """  """
        pass