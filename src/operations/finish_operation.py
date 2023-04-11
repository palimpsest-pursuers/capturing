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
        self.main.thread.start()


    def finished(self):
        self.main.thread.quit()

    def cancel(self):
        self.main.thread.quit()

class FinishWorker(QObject):
    main = None
    
    def run(self):
        destination_dir = QFileDialog.getExistingDirectory()

        name = self.main.metadata["title"]
        name = name.replace(' ', "_")

        #generate xml (once)
        metadata_xml = dict2xml({"metadata": self.main.metadata})
        with open(destination_dir + "\\" + name +"-metadata.xml", "w") as file:
            file.write(metadata_xml)

        self.main.cube_builder.build(destination_dir, name)
        self.main.finish_op.finished()