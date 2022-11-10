from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class LightLevelMode(Operation):
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
        print("Light level mode on")
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11], '100') #630 nm (red)
        image100 = self.ui.camera_control.run()
        self.ui.LightDisplayTL.setPixmap(QPixmap.fromImage(image100))
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11], '75') #630 nm (red)
        image75 = self.ui.camera_control.run()
        self.ui.LightDisplayTR.setPixmap(QPixmap.fromImage(image75))
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11], '50') #630 nm (red)
        image50 = self.ui.camera_control.run()
        self.ui.LightDisplayBL.setPixmap(QPixmap.fromImage(image50))
        self.ui.led_control.turn_on(self.ui.led_control.wavelength_list[11], '25') #630 nm (red)
        image25 = self.ui.camera_control.run()
        self.ui.LightDisplayBR.setPixmap(QPixmap.fromImage(image25))

    def cancel(self):
        """"""
        self.ui.infobox.setText('Operation Canceled')
        self.ui.led_control.turn_off()
        self.ui.change_operation(self.ui.idle_op)

    def set_infobox(self):
        """  """
        self.ui.infobox.setText("LEVEL!")

    def big_display():
        """  """
        pass
    
    def small_top_display(self):
        """  """
        pass

    def small_middle_display(self):
        """  """
        pass