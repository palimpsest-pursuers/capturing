import serial

class LEDController:

    #wavelengths for the LEDs on the boards in nanometers (nm)
    wavelength_list = ['356', '385', '395', '420',
                       '450', '470', '490', '520', 
                       '560', '590', '615', '630', 
                       '660', '730', '850', '940']
    def __init__(self):
        """Open up the connection to LED's serial port"""
        self.led_connection = serial.Serial('COM3', 9600)
        
        if(not self.led_connection.isOpen()):
            self.led_connection.open()

    def disconnect(self):
        """Close the connection to the LED's serial port"""
        self.led_connection.close()

    def turn_on(self, wavelength, intensity):
        """
        Turn on a specific LED using wavelength
        The LED board accepts commands written as:
            'wavelength,intensity\\n'
        For our purposes, the intensity will always be 100
        Edit 11/10 added preliminary intensity value
        """
        command = (wavelength + ',' + intensity + '\n')
        print(command)
        print(command.encode())
        self.led_connection.write((wavelength + ',' + intensity + '\n').encode())

    def turn_off(self):
        """Turn off all LEDs"""
        self.led_connection.write(('0,0\n').encode())


if __name__ == '__main__':
    lc = LEDController()
    print(lc.led_connection.isOpen())
    lc.turn_on('630', '100')
    lc.turn_on('630', '75')
    lc.turn_on('630', '50')
    lc.turn_on('630', '25')
    lc.turn_on('630', '10')
    lc.turn_off()