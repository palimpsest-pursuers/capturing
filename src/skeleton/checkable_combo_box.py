from PyQt5 import QtWidgets, QtCore

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # make the combo editable so the user can type
        self.setEditable(True)
        # when they hit Enter, we’ll grab the text and add it
        self.lineEdit().returnPressed.connect(self._on_return_pressed)

    def addItem(self, text):
        """Override so every new item gets a checkbox."""
        super().addItem(text)
        item = self.model().item(self.count()-1, 0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)

    def _on_return_pressed(self):
        """Called when the user presses Enter in the line edit."""
        text = self.currentText().strip()
        # only add non-empty, non-duplicate entries
        if text and self.findText(text) == -1:
            self.addItem(text)
        # clear the edit field
        self.clearEditText()

    def itemChecked(self, index):
        """Check whether the given index is checked."""
        item = self.model().item(index, 0)
        return item.checkState() == QtCore.Qt.Checked