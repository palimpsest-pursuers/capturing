from abc import ABC, abstractmethod

'''
LED Interface
Written by Sai Keshav Sasanapuri, Cecelia Ahrens, and Mallory Bridge
'''


class LEDInterface(ABC):
    # wavelengths for the LEDs on the boards in nanometers (nm) DEFAULT
    wavelength_list = ['365', '385', '395', '420',
                       '450', '470', '500', '530',
                       '560', '590', '615', '630',
                       '660', '730', '850', '940']

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def turn_on(self, wavelength) -> None:
        pass

    def turn_off(self) -> None:
        pass
