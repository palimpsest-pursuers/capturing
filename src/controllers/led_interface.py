from abc import ABC, abstractmethod

class LEDInterface(ABC):
    #wavelengths for the LEDs on the boards in nanometers (nm)
    wavelength_list = ['356', '385', '395', '420',
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
