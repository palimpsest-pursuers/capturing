from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog
import sys, os


class MetadataEntryDialog(QtWidgets.QDialog):
    def __init__(self, operation, parent=None):
        # self._ui_path = RELATIVE_PATH + "/skeleton"  
        super().__init__(parent)
        uic.loadUi("./skeleton/metadata-dialog.ui", self)

        # self.buttonBox.accepted.connect(lambda: print("accept"))
        # self.buttonBox.rejected.connect(lambda: print("reject"))


        
        

