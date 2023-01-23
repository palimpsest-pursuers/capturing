from abc import ABC, abstractmethod

class Operation(ABC):
    """
    Interface for operation modes
    """
    
    def set_ui(self, ui) -> None:
        self.ui = ui
    
    @abstractmethod
    def on_start(self) -> None:
        """ """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """ """
        pass