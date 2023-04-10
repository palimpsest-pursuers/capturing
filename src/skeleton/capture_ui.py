from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setMaximumSize(16777215, 16777215)
        self.centralwidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.layout = QtWidgets.QStackedLayout()
        self.centralwidget.setLayout(self.layout)
        self.page1 = QtWidgets.QWidget()
        self.page1.setLayout(QtWidgets.QVBoxLayout())
        self.page1.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.button1 = QtWidgets.QPushButton(self.page1)
        self.button1.setText('1')
        self.button1.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.page2 = QtWidgets.QWidget()
        self.page2.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.page2.setLayout(QtWidgets.QVBoxLayout())
        self.button2 = QtWidgets.QPushButton(self.page2)
        self.button2.setText('2')
        self.button2.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.page1)
        self.layout.addWidget(self.page2)

        self.page3 = QtWidgets.QWidget()
        #self.page3.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.layout2 = QtWidgets.QVBoxLayout()
        self.page3.setLayout(self.layout2)

        self.top = QtWidgets.QFrame()
        btPolicy = QtWidgets.QSizePolicy()
        btPolicy.setVerticalStretch(1)
        btPolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.top.setSizePolicy(btPolicy)

        mPolicy = QtWidgets.QSizePolicy()
        mPolicy.setVerticalStretch(6)
        mPolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.middle = QtWidgets.QFrame()
        self.middle.setSizePolicy(mPolicy)

        self.bottom = QtWidgets.QFrame()
        self.bottom.setSizePolicy(btPolicy)

        self.layout2.addChildWidget(self.top)
        self.layout2.addChildWidget(self.middle)
        self.layout2.addChildWidget(self.bottom)

        self.top.setStyleSheet("background-color: #262626;")
        self.middle.setStyleSheet("background-color: #262626;")
        self.bottom.setStyleSheet("background-color: #262626;")

        self.page2.setStyleSheet("background-color: #505050;")

        self.layout.addWidget(self.page3)

        self.button1.clicked.connect(lambda: self.button1clicked())
        self.button2.clicked.connect(lambda: self.button2clicked())
        
        self.layout.setCurrentWidget(self.page1)


    def button1clicked(self):
        print('1 pressed')
        self.layout.setCurrentWidget(self.page2)

    def button2clicked(self):
        print('2 pressed')
        self.layout.setCurrentWidget(self.page3)

    def create_page_widget(self, name=str):
        page = QtWidgets.QWidget()
        page.setObjectName(name)
        page.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        layout = QtWidgets.QVBoxLayout()
        page.setLayout(layout)

        top = QtWidgets.QPushButton("TOP")
        btPolicy = QtWidgets.QSizePolicy()
        btPolicy.setVerticalStretch(1)
        btPolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        top.setSizePolicy(btPolicy)

        mPolicy = QtWidgets.QSizePolicy()
        mPolicy.setVerticalStretch(6)
        mPolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        middle = QtWidgets.QPushButton("MIDDLE")
        middle.setSizePolicy(mPolicy)

        bottom = QtWidgets.QPushButton("BOTTOM")
        bottom.setSizePolicy(btPolicy)

        top.setObjectName(name +'Top')
        middle.setObjectName(name +'Middle')
        bottom.setObjectName(name +'Bottom')

        layout.addWidget(top)
        layout.addWidget(middle)
        layout.addWidget(bottom)

        top.setStyleSheet("background-color: #262626;")
        middle.setStyleSheet("background-color: #262626;")
        bottom.setStyleSheet("background-color: #262626;")

        return page
        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setMaximumSize(16777215, 16777215)
    MainWindow.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())