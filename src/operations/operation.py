from abc import ABC, abstractmethod

class Operation(ABC):
    """
    Interface for operation modes
    """
    
    def set_ui(self, ui) -> None:
        self.ui = ui
    
    @abstractmethod
    def on_start(self, metadata) -> None:
        """ """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """ """
        pass

    #@abstractmethod
    def finished(self) -> None:
        """ """
        self.ui.infobox.setText('Operation Finished')
        self.ui.thread.quit()
        self.ui.change_operation(self.ui.idle_op)
