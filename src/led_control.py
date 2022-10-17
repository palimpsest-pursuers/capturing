import serial

class LEDController:

    #wavelengths for the LEDs on the boards in nanometers (nm)
    wavelength_list = [356, 385, 395, 420,
                       450, 470, 490, 520, 
                       560, 590, 615, 630, 
                       660, 730, 850, 940]

    def __init__(self):
        """Open up the connection to LED's serial port"""
        self.led_connection = serial.Serial('COM3', 9600)
        
        if(not self.led_connection.isOpen()):
            self.led_connection.open()

    def disconnect(self):
        """Close the connection to the LED's serial port"""
        self.led_connection.close()

    def turn_on(self, wavelength):
        """
        Turn on a specific LED using wavelength
        The LED board accepts commands written as:
            'wavelength,intensity\n'
        For our purposes, the intensity will always be 100
        """
        self.led_connection.write(wavelength + ',100\n')

    def turn_off(self):
        """Turn off all LEDs"""
        self.led_connection.write('0,0\n')

    