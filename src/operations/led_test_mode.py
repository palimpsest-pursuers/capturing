import time

def cycle_wavelengths(window, led_control):

    #Only cycle through the wavelengths that are visible
    for wavelength in led_control.wavelength_list[4:12]:
        old_text = str(window.infobox.text())
        print(old_text)
        next_line = "\n".join([old_text, "Testing: " + wavelength + "nm"])
        window.infobox.setText(next_line)
        window.update()
        led_control.turn_on(wavelength)
        time.sleep(1)
        led_control.turn_off()

def click_TestLEDs(window, led_control):
    print(window)
    window.FocusButton.setEnabled(False)
    window.CaptureButton.setEnabled(False)
    window.FlatsButton.setEnabled(False)
    window.CancelButton.setEnabled(True)
    window.infobox.setText("Testing LEDs")
    cycle_wavelengths(window, led_control)

if __name__ == '__main__':
    cycle_wavelengths(None)