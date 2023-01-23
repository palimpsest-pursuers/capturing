from controllers.led_controller import LEDController

class LEDMock(LEDController):

    def __init__(self):
        print("Mock LED connected")

    def disconnect(self):
        print("Mock LED disconnected")

    def turn_on(self, wavelength):
        command = (wavelength + ',100\n')
        print(command)
    
    def turn_off(self):
        print('0,0\n')