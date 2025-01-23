from controllers.led_interface import LEDInterface

'''
Mock LEDs for Testing Purposes 
Written by Cecelia Ahrens
'''
class LEDMock(LEDInterface):

    def __init__(self):
        pass

    def disconnect(self):
        pass

    def turn_on(self, wavelength):
        command = (wavelength + ',100\n')
    
    def turn_off(self):
        pass