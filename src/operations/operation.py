from abc import ABC, abstractmethod

class Operation(ABC):
    """
    Interface for operation modes
    """
    
    def set_main(self, main) -> None:
        self.main = main
    
    @abstractmethod
    def on_start(self) -> None:
        """ """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """ """
        pass

    #@abstractmethod
    def finished(self) -> None:
        """ """
        #self.ui.infobox.setText('Operation Finished')
        self.main.thread.quit()
        #self.ui.change_operation(self.ui.idle_op)
