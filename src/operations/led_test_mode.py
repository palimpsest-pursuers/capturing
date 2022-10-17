import time

#from src.skeleton.TestLEDs import UI_MainWindow
from led_control import LEDController

def cycle_wavelengths(UI_MainWindow):
    led_control =  LEDController

    #TODO: Check which ones are visiable, slice the list
    for wavelength in led_control.wavelength_list:
        old_text = UI_MainWindow.infobox.text
        next_line = "\n".join([old_text, "Testing: " + wavelength + "nm"])
        UI_MainWindow.infobox.setText(next_line)
        #led_control.turn_on(wavelength)
        time.sleep(1)
        #led_control.turn_off

def click_TestLEDs(UI_MainWindow):
    UI_MainWindow.FocusButton.setEnabled(False)
    UI_MainWindow.CaptureButton.setEnabled(False)
    UI_MainWindow.FlatsButton.setEnabled(False)
    UI_MainWindow.CancelButton.setEnabled(True)
    UI_MainWindow.infobox.setText("Testing LEDs")
    cycle_wavelengths(UI_MainWindow)