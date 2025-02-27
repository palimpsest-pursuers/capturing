from PyQt5 import uic, QtWidgets, QtCore

class CheckableComboBox(QtWidgets.QComboBox):
    # once there is a checkState set, it is rendered
    # here we assume default Unchecked
    def addItem(self, item):
        super(CheckableComboBox, self).addItem(item)
        item = self.model().item(self.count()-1,0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)

    def itemChecked(self, index):
        item = self.model().item(index,0)
        return item.checkState() == QtCore.Qt.Checked