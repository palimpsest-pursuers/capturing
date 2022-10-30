from abc import ABC, abstractmethod

class Operation(ABC):
    """
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

    @abstractmethod
    def set_infobox(self) -> None:
        """  """
        pass

    @abstractmethod
    def big_display(self) -> None:
        """  """
        pass
    
    @abstractmethod
    def small_top_display(self) -> None:
        """  """
        pass

    @abstractmethod
    def small_middle_display(self) -> None:
        """  """
        pass