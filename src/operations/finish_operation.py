from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from dict2xml import dict2xml

class FinishOp(Operation):
    main = None
    def on_start(self):
        self.main.thread = QThread()
        self.main.worker = FinishWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.main.thread.started.connect(self.main.worker.run)
        self.main.worker.finished.connect(self.finished)
        self.main.thread.start()
        #self.main.cube_builder.build("C:\\Users\\cecel\\SeniorProject\\capturing\\Test", "Testing")
        


    def finished(self, error):
        self.main.thread.quit()
        if error == '':
            self.main.finishDone()
        else:
            self.main.finishInfoText.setText(error)

    def cancel(self):
        self.main.thread.quit()

class FinishWorker(QObject):
    main = None
    
    finished = pyqtSignal(str)
    
    def run(self):
        try:
            destination_dir = QFileDialog.getExistingDirectory()
        except:
            self.finished.emit("You must choose a destination folder to save cube.")

        name = self.main.metadata["title"]
        name = name.replace(' ', "_")

        #generate xml (once)
        metadata_xml = dict2xml({"metadata": self.main.metadata})
        with open(destination_dir + "\\" + name +"-metadata.xml", "w") as file:
            file.write(metadata_xml)
        build_result = self.main.cube_builder.build(destination_dir, name)
        if build_result == None:
            self.finished.emit('')
        else: 
            self.finished.emit(build_result)