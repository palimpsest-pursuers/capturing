from abc import ABC, abstractmethod

'''
Interface for MISHA Image Capturing Operations
Written by Cecelia Ahrens
'''
class Operation(ABC):

    """Gives access to UI"""
    def set_main(self, main) -> None:
        self.main = main
    
    @abstractmethod
    def on_start(self) -> None:
        pass

    @abstractmethod
    def cancel(self) -> None:
        pass

    
    def finished(self) -> None:
        self.main.thread.quit()
