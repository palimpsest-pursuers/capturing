import sys, os
from PyQt5 import uic, QtWidgets, QtCore, QtGui

print("START")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    ui_path = os.path.join(os.path.dirname(__file__), 'skeleton/capture-mode2.ui')
    uic.loadUi(ui_path, window)
    
    TestLedsButton = QtWidgets.QPushButton('TestLedsButton')
    
    window.show()
    sys.exit(app.exec_())