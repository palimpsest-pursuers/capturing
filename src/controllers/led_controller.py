import serial
import serial.tools.list_ports
import time
from controllers.led_interface import LEDInterface

'''
LED Controller for Controlling LED board
Written by Cecelia Ahrens, and Mallory Bridge
'''
class LEDController(LEDInterface):

    '''Initialize and connect to LED board'''
    def __init__(self):
        """Open up the connection to LED's serial port"""

        port_number = 'COM3' #default port number for LED board

        #This looks for the port name (e.g., COM4) after the virual com's name
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if("Silicon Labs CP210x USB to UART Bridge") in port.description:
                port_number = port.device
                break
        self.led_connection = serial.Serial(port_number, 9600)
        
        if(not self.led_connection.isOpen()):
            self.led_connection.open()

    def disconnect(self):
        """Close the connection to the LED's serial port"""
        self.led_connection.close()

    def turn_on(self, wavelength):
        """
        Turn on a specific LED using wavelength
        The LED board accepts commands written as:
            'wavelength,intensity\\n'
        For our purposes, the intensity will always be 100
        """
        command = (wavelength + ',100\n')
        print(command)
        self.led_connection.write((wavelength + ',100\n').encode())

    def turn_off(self):
        """Turn off all LEDs"""
        self.led_connection.write(('0,0\n').encode())


if __name__ == '__main__':
    lc = LEDController()
    print(lc.led_connection.isOpen())
    
    for x in lc.wavelength_list:
        lc.turn_on(x)
        time.sleep(0.5)

    lc.turn_off()