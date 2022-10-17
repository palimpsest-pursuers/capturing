import time
from led_control import LEDController

def cycle_wavelengths():
    led_control =  LEDController

    #TODO: Check which ones are visiable, slice the list
    for wavelength in led_control.wavelength_list:
        led_control.turn_on(wavelength)
        time.sleep(1)
        led_control.turn_off
