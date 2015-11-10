import sys
from os import path, sep, mkdir
import crypto
from shutil import copy2
from PyQt4 import uic
from PyQt4.QtGui import QApplication, QFileSystemModel, QMessageBox, QInputDialog, QLineEdit, QMenu
from PyQt4.QtCore import Qt
from checkable_dir import CheckableDirModel
from file_types_window import FileTypes
from threading import Thread, Lock
from time import sleep
from checkable_storage import Model as StorageModel

base, form = uic.loadUiType("design"+sep+"secure_usb_backup.ui")
class MainWindow(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.resize(600, 500)
        self.model_computer = CheckableDirModel()
        self.treeViewComputer.setModel(self.model_computer)
        self.treeViewComputer.setIndentation(10)
        self.treeViewComputer.setSortingEnabled(True)
        self.treeViewComputer.setColumnWidth(0, 200)
        self.treeViewComputer.setColumnWidth(1, 80)
        self.treeViewComputer.setColumnWidth(2, 80)

        # some staff
        self.system_encoding = sys.getfilesystemencoding()
        self.files = {}
        self.selected_file_types = {}
        self.lock = Lock()
        self.threads = []

        self.model_storage = StorageModel()
        if not path.exists(path.dirname(path.abspath(__file__)) + sep + "All BackUps"):
            mkdir(path.dirname(path.abspath(__file__)) + sep + "All BackUps")
        self.model_storage.setRootPath(path.dirname(path.abspath(__file__)).decode(self.system_encoding) + sep + "All BackUps")
        self.treeViewStorage.setModel(self.model_storage)
        self.treeViewStorage.setRootIndex(self.model_storage.index(self.model_storage.rootPath()))
        self.treeViewStorage.setIndentation(10)
        self.treeViewStorage.setSortingEnabled(True)
        self.treeViewStorage.setColumnWidth(0, 200)
        self.treeViewStorage.setColumnWidth(1, 80)
        self.treeViewStorage.setColumnWidth(2, 80)
        self.treeViewStorage.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeViewStorage.customContextMenuRequested.connect(self.openMenu)

        # buttons
        self.scanButton.clicked.connect(self.scan)
        self.fileTypesButton.clicked.connect(self.select_file_types)
        self.backupButtonComp.clicked.connect(self.backup)
        self.backupButtonStorage.clicked.connect(self.backup)
        self.tabWidgetRoot.setCurrentWidget(self.tab_computer)

    def scan(self):
        self.treeViewComputer.setEnabled(False)
        self.backupButtonComp.setEnabled(False)
        self.fileTypesButton.setEnabled(False)

        if not self.selected_file_types:
            dialog = FileTypes(self)
            dialog.show()
            return
        for element in self.selected_file_types:
            selected = []
            for _type, state in element["Types"].items():
                if state == Qt.Checked:
                    selected.append(_type)
            if selected:
                for index, state in self.model_computer.checks.items():
                    self.files.update({element.keys()[0]: []})
                    print("start tread for %s" % element.keys()[0])
                    th = Thread(target=self.model_computer.exportChecked, args=(self.lock,
                                                                       {index: state},
                                                                       element.keys()[0],
                                                                       selected, self.files))
                    th.start()
                    self.threads.append(th)

        status = map(Thread.isAlive, self.threads)
        while any(status):
            status = map(Thread.isAlive, self.threads)
            sleep(.5)
            self.filesFoundLabel.setText("Scaning.")
            sleep(.5)
            self.filesFoundLabel.setText("Scaning..")
            sleep(.5)
            self.filesFoundLabel.setText("Scaning...")
        self.filesFoundLabel.setText("Scaning finished! Files found %s" % sum(len(v) for k, v in self.files.items()))

        self.treeViewComputer.setEnabled(True)
        self.backupButtonComp.setEnabled(True)
        self.fileTypesButton.setEnabled(True)

    def backup(self):
        try:
            selected = self.treeViewStorage.selectedIndexes()[0]
            warehouse = self.model_storage.filePath(selected).split('/')[-1]
            #print(self.model_storage.filePath(selected).split('/')[-1])
            key, ok = QInputDialog.getText(self,
                            "Key",
                            "Enter key for <b>%s</b> storage" % warehouse,
                            mode=QLineEdit.Password)
            if ok: # and hash(key) == hash from storage
                for category, files in self.files.items():
                    current_dir = path.dirname(path.abspath(__file__)).decode(self.system_encoding) + sep \
                                  + "All BackUps" + sep + warehouse + sep + category
                    if not path.exists(current_dir):
                        mkdir(current_dir)
                    for _file in files:
                        copy2(_file, current_dir)

        except IndexError:
            QMessageBox.about(self, "Error", "Select the storage before creating backup!")
            self.tabWidgetRoot.setCurrentWidget(self.tab_storage)

    def openMenu(self, position):
        level = 0
        index = self.treeViewStorage.selectedIndexes()[0]
        while index.parent().isValid():
            index = index.parent()
            level += 1

        menu = QMenu()
        #if level == 0:
        menu.addAction(self.tr("Add storage"), self.add_storage)


        menu.exec_(self.treeViewStorage.viewport().mapToGlobal(position))

    def add_storage(self):
        pass

    def select_file_types(self):
        dialog = FileTypes(self)
        dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
