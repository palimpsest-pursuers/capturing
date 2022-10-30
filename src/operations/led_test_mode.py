from itertools import cycle
import time
from threading import Thread
from operations.operation import Operation

class TestLEDMode(Operation):
    """
    """
    ui = None
    cancelled = False

    def on_start(self):
        """"""
        self.ui.CaptureButton.setEnabled(False)
        self.ui.TestLedsButton.setEnabled(False)
        self.ui.FlatsButton.setEnabled(False)
        self.ui.FocusButton.setEnabled(False)
        self.ui.LightLevelsButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(False)
        self.ui.infobox.setText("Testing LEDs")
        #thread = Thread(target=self.cycle_wavelengths())
        #thread.run()
        self.cycle_wavelengths()
        
    def cancel(self):
        """"""
        self.cancel = True
        self.ui.infobox.setText('Operation Canceled')
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

    def cycle_wavelengths(self):

        #Only cycle through the wavelengths that are visible
        for wavelength in self.ui.led_control.wavelength_list[4:12]:
            old_text = str(self.ui.infobox.text())
            print(old_text)
            next_line = "\n".join([old_text, "Testing: " + wavelength + "nm"])
            self.ui.infobox.setText(next_line)
            self.ui.update()
            self.ui.led_control.turn_on(wavelength)
            i = 0
            while i <= 1:
                #if self.cancelled:
                #    return
                time.sleep(0.1)
                i = i + 0.1
            self.ui.led_control.turn_off()
'''
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
'''