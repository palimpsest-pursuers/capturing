from operations.operation import Operation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from dict2xml import dict2xml

'''
Finish Operation for Building the Cube and Saving All Data
Written by Cecelia Ahrens, and Robert Maron
'''
class FinishOp(Operation):
    main = None

    '''Starts Finish Operation'''
    def on_start(self):
        # start thread, move worker to thread
        self.main.thread = QThread()
        self.main.worker = FinishWorker()
        self.main.worker.moveToThread(self.main.thread)
        self.main.worker.main = self.main
        self.main.thread.started.connect(self.main.worker.run)

        # connect slots
        self.main.worker.finished.connect(self.finished)

        # start
        self.main.thread.start()
        

    '''Finish Operation'''
    def finished(self, error):
        self.main.thread.quit()
        if error == '':
            self.main.finishDone()
        else:
            self.main.finishInfoText.setText(error)

    '''Cancel Operation'''
    def cancel(self):
        self.main.thread.quit()

class FinishWorker(QObject):
    main = None
    finished = pyqtSignal(str)
    
    def run(self):
        # dialog for user selection of output directory
        try:
            destination_dir = QFileDialog.getExistingDirectory()
        except:
            self.finished.emit("You must choose a destination folder to save cube.")

        # cleaning up object title for saving data
        name = self.main.metadata["title"]
        name = name.replace(' ', "_")

        #generate xml (once)
        metadata_xml = dict2xml({"metadata": self.main.metadata})
        with open(destination_dir + "\\" + name +"-metadata.xml", "w") as file:
            file.write(metadata_xml)
        
        #build and save cube and images
        build_result = self.main.cube_builder.build(destination_dir, name)
        if build_result == None:
            self.finished.emit('')
        else: 
            self.finished.emit(build_result)

        self.main.finishFinishButton.setEnabled(True)
        self.main.finishCancelButton.setEnabled(True)
        self.main.finishRedoButton.setEnabled(True)
        self.main.finishComboBox.setEnabled(True)
        self.finishInfoText.setEnabled(True)