from operations.operation import Operation
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from dict2xml import dict2xml

'''
Finish Operation for Building the Cube and Saving All Data
Written by Sai Keshav Sasanapuri, Cecelia Ahrens, and Robert Maron
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
        self.main.worker.progress_box.connect(self.updateProgressDialog)

        # start
        self.main.thread.start()

    '''Finish Operation'''

    def finished(self, error):
        self.main.thread.quit()
        if error != '':
            self.main.finishInfoText.setText(error)

    '''Cancel Operation'''

    def cancel(self):
        self.main.thread.quit()

    '''Start or Stop Progress dialog box'''

    def updateProgressDialog(self, message):
        if message == "close":
            self.main.progress_box.stop()
        else:
            self.main.progress_box.start(message)


class FinishWorker(QObject):
    main = None
    finished = pyqtSignal(str)
    progress_box = pyqtSignal(str)

    def run(self):
        self.main.finishPageTitle.setText("Saving Cube in the selected folder")
        # dialog for user selection of output directory
        destination_dir = None
        try:
            destination_dir = QFileDialog.getExistingDirectory()
        except:
            pass
        if destination_dir is not None and destination_dir != "":
            self.progress_box.emit("Saving cube")
            # cleaning up object title for saving data
            name = self.main.metadata["title"]
            name = name.replace(' ', "_")
            name = f"{name}_DataCube"

            # generate xml (once)
            metadata_xml = dict2xml({"metadata": self.main.metadata})
            with open(destination_dir + "\\" + name + "-metadata.xml", "w") as file:
                file.write(metadata_xml)

            # save exposure profile
            self.main.light_op.saveProfile("MISHA_ExposureProfile", destination_dir)

            # build and save cube and images
            build_result = self.main.cube_builder.build(destination_dir, name)
            if build_result == None:
                self.finished.emit('')
            else:
                self.finished.emit(build_result)
            self.main.finishPageTitle.setText("Cube saved in selected folder")
        else:
            self.finished.emit('Failed to save cube')
            self.main.finishPageTitle.setText("Save Cropped Image Cube in ENVI Format")
        self.progress_box.emit("close")
        self.main.finishFinishButton.setEnabled(True)
        self.main.finishRedoButton.setEnabled(True)
        self.main.finishComboBox.setEnabled(True)
        self.main.finishInfoText.setEnabled(True)
        self.main.finishStartOverButton.setEnabled(True)
