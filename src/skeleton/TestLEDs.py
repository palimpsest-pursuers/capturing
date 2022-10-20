# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'capture-mode2.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import resources_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1076, 604)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.operationsBox = QtWidgets.QGroupBox(self.centralwidget)
        self.operationsBox.setGeometry(QtCore.QRect(10, 10, 131, 551))
        self.operationsBox.setObjectName("operationsBox")
        self.FocusButton = QtWidgets.QPushButton(self.operationsBox)
        self.FocusButton.setGeometry(QtCore.QRect(20, 20, 93, 28))
        self.FocusButton.setObjectName("FocusButton")
        self.CaptureButton = QtWidgets.QPushButton(self.operationsBox)
        self.CaptureButton.setEnabled(False)
        self.CaptureButton.setGeometry(QtCore.QRect(20, 60, 93, 28))
        self.CaptureButton.setObjectName("CaptureButton")
        self.FlatsButton = QtWidgets.QPushButton(self.operationsBox)
        self.FlatsButton.setEnabled(False)
        self.FlatsButton.setGeometry(QtCore.QRect(20, 100, 93, 28))
        self.FlatsButton.setObjectName("FlatsButton")
        self.TestLedsButton = QtWidgets.QPushButton(self.operationsBox)
        self.TestLedsButton.setEnabled(True)
        self.TestLedsButton.setGeometry(QtCore.QRect(20, 140, 93, 28))
        self.TestLedsButton.setToolTip("")
        self.TestLedsButton.setToolTipDuration(-1)
        self.TestLedsButton.setCheckable(True)
        self.TestLedsButton.setObjectName("TestLedsButton")
        self.TestLedsButton.clicked.connect(self.testLEDsMode)
        self.LightLevelsButton = QtWidgets.QPushButton(self.operationsBox)
        self.LightLevelsButton.setEnabled(False)
        self.LightLevelsButton.setGeometry(QtCore.QRect(20, 180, 93, 28))
        self.LightLevelsButton.setObjectName("LightLevelsButton")
        self.CancelButton = QtWidgets.QPushButton(self.operationsBox)
        self.CancelButton.setGeometry(QtCore.QRect(20, 510, 93, 28))
        self.CancelButton.setObjectName("CancelButton")
        self.LargeDisplay = QtWidgets.QLabel(self.centralwidget)
        self.LargeDisplay.setGeometry(QtCore.QRect(160, 20, 631, 541))
        self.LargeDisplay.setAutoFillBackground(False)
        self.LargeDisplay.setText("")
        self.LargeDisplay.setScaledContents(True)
        self.LargeDisplay.setObjectName("LargeDisplay")
        self.middleRightDisplay = QtWidgets.QLabel(self.centralwidget)
        self.middleRightDisplay.setGeometry(QtCore.QRect(820, 180, 251, 191))
        self.middleRightDisplay.setAutoFillBackground(False)
        self.middleRightDisplay.setText("")
        self.middleRightDisplay.setScaledContents(True)
        self.middleRightDisplay.setObjectName("middleRightDisplay")
        self.TopRightLabel = QtWidgets.QLabel(self.centralwidget)
        self.TopRightLabel.setGeometry(QtCore.QRect(910, 10, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.TopRightLabel.setFont(font)
        self.TopRightLabel.setObjectName("TopRightLabel")
        self.TopRightDisplay = QtWidgets.QLabel(self.centralwidget)
        self.TopRightDisplay.setGeometry(QtCore.QRect(820, 40, 251, 131))
        self.TopRightDisplay.setAutoFillBackground(False)
        self.TopRightDisplay.setText("")
        self.TopRightDisplay.setScaledContents(True)
        self.TopRightDisplay.setObjectName("TopRightDisplay")
        self.infobox = QtWidgets.QLabel(self.centralwidget)
        self.infobox.setGeometry(QtCore.QRect(820, 380, 251, 181))
        self.infobox.setAutoFillBackground(False)
        self.infobox.setStyleSheet("#infobox{\n"
"    background-color:white;\n"
"    border: 1px solid;\n"
"    border-color:#eeeeee;\n"
"}")
        self.infobox.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.infobox.setIndent(-1)
        self.infobox.setObjectName("infobox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1076, 18))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSave_as = QtWidgets.QMenu(self.menuFile)
        self.menuSave_as.setObjectName("menuSave_as")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionCube = QtWidgets.QAction(MainWindow)
        self.actionCube.setObjectName("actionCube")
        self.menuSave_as.addAction(self.actionCube)
        self.menuFile.addAction(self.menuSave_as.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    
    def testLEDsMode(self):
        led_test_mode.click_TestLEDs(self);

    def cancel(self):
        self.FocusButton.setEnabled(True)
        self.CaptureButton.setEnabled(True)
        self.FlatsButton.setEnabled(True)
        self.TestLedsButton.setEnabled(True)
        self.LightLevelsButton.setEnabled(True)
        self.CancelButton.setEnabled(True)
        self.TopRightLabel.setVisible(False)
        self.infobox.setText("")


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MISHA Image Capture"))
        self.operationsBox.setTitle(_translate("MainWindow", "Operations"))
        self.FocusButton.setText(_translate("MainWindow", "Focus"))
        self.CaptureButton.setText(_translate("MainWindow", "Capture Images"))
        self.FlatsButton.setText(_translate("MainWindow", "Capture Flats"))
        self.TestLedsButton.setText(_translate("MainWindow", "Test LEDs"))
        self.LightLevelsButton.setText(_translate("MainWindow", "Light Levels"))
        self.CancelButton.setText(_translate("MainWindow", "Cancel"))
        self.TopRightLabel.setText(_translate("MainWindow", "Histogram"))
        self.infobox.setText(_translate("MainWindow", "Infobox Information"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuSave_as.setTitle(_translate("MainWindow", "Save as..."))
        self.actionCube.setText(_translate("MainWindow", "Cube"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.cancel()
    sys.exit(app.exec_())