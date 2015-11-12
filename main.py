import sys, datetime
from os import path, sep, mkdir
import crypto
from shutil import copy2
from PyQt4 import uic
from PyQt4.QtGui import QApplication, QFileSystemModel, QMessageBox, QInputDialog, QLineEdit, QDialog, QTreeView
from PyQt4.QtCore import Qt
from checkable_dir import CheckableDirModel
from file_types_window import FileTypes
from new_storage_dialog import NewStorage
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
        self.password = ''
        self.selected_storage = ''
        self.files = {}
        self.selected_file_types = {}
        self.lock = Lock()
        self.threads = []

        self.model_storage = StorageModel()
        if not path.exists(path.dirname(path.abspath(__file__)) + sep + "All BackUps"):
            mkdir(path.dirname(path.abspath(__file__)) + sep + "All BackUps")
        self.current_dir = path.dirname(path.abspath(__file__)).decode(self.system_encoding) + sep + "All BackUps" + sep
        self.model_storage.setRootPath(path.dirname(path.abspath(__file__)).decode(self.system_encoding) + sep + "All BackUps")
        self.treeViewStorage.setModel(self.model_storage)
        self.treeViewStorage.setRootIndex(self.model_storage.index(self.model_storage.rootPath()))
        self.treeViewStorage.setIndentation(10)
        self.treeViewStorage.setSortingEnabled(True)
        self.treeViewStorage.setColumnWidth(0, 200)
        self.treeViewStorage.setColumnWidth(1, 80)
        self.treeViewStorage.setColumnWidth(2, 80)


        # buttons
        self.scanButton.clicked.connect(self.scan)
        self.fileTypesButton.clicked.connect(self.select_file_types)
        self.backupButtonComp.clicked.connect(self.backup)
        self.backupButtonStorage.clicked.connect(self.backup)
        #self.tabWidgetRoot.setCurrentWidget(self.tab_storage)
        self.newStorageButton.clicked.connect(self.add_storage)
        self.helpButtonComputer.clicked.connect(self.help)

    def help(self):
        print(self.selected_file_types)

    def scan(self):
        self.treeViewComputer.setEnabled(False)
        self.backupButtonComp.setEnabled(False)
        self.fileTypesButton.setEnabled(False)
        self.files = {}
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
            selected_index = self.treeViewStorage.selectedIndexes()[0]
            selected_path = self.model_storage.filePath(selected_index).split('/')[::-1]
            warehouse = ''
            for i, dir in enumerate(selected_path):
                if dir == "All BackUps":
                    warehouse = str(selected_path[i-1])

            #print(str(self.model_storage.filePath(selected_index).split('/')))
            #warehouse = str(self.model_storage.filePath(selected_index).split('/')[-1])
            key_from_storage = open(self.current_dir + warehouse + sep + "key.txt", 'r').read()

            if self.selected_storage == warehouse and self.password == key_from_storage:
                now_date = datetime.datetime.now().strftime('Backup_%m-%d-%y_%H-%M')
                mkdir(self.current_dir + warehouse + sep + now_date + sep)
                for category, files in self.files.items():
                    current_dir = self.current_dir + warehouse + sep + now_date + sep + category
                    if not path.exists(current_dir):
                        mkdir(current_dir)
                    for _file in files:
                        copy2(_file, current_dir)
            else:
                key, ok = QInputDialog.getText(self, "Key", "Enter key for <b>%s</b> storage" % warehouse,
                                               mode=QLineEdit.Password)
                if ok:
                    if key == key_from_storage: # and hash(key) == hash from key.txt
                        now_date = datetime.datetime.now().strftime('Backup_%m-%d-%y_%H-%M')
                        mkdir(self.current_dir + warehouse + sep + now_date + sep)
                        for category, files in self.files.items():
                            current_dir = self.current_dir + warehouse + sep + now_date + sep + category
                            if not path.exists(current_dir):
                                mkdir(current_dir)
                            for _file in files:
                                copy2(_file, current_dir)
                    else:
                        QMessageBox.about(self, "Error", "Incorrect password!")

        except IndexError:
            if self.selected_storage:
                key_from_storage = open(self.current_dir + self.selected_storage + sep + "key.txt", 'r').read()
                if self.password == key_from_storage:
                    now_date = datetime.datetime.now().strftime('Backup_%m-%d-%y_%H-%M')
                    mkdir(self.current_dir + self.selected_storage + sep + now_date + sep)
                    for category, files in self.files.items():
                        current_dir = self.current_dir + self.selected_storage + sep + now_date + sep + category
                        if not path.exists(current_dir):
                            mkdir(current_dir)
                        for _file in files:
                            copy2(_file, current_dir)
            else:
                QMessageBox.about(self, "Error", "Select the storage before creating backup!")
                self.tabWidgetRoot.setCurrentWidget(self.tab_storage)
        except WindowsError:
            QMessageBox.about(self, "Error", "Too little time for previous backup!\nWait a minute, please.")

    def add_storage(self):
        dialog = NewStorage(self)
        dialog.show()


    def select_file_types(self):
        dialog = FileTypes(self)
        dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
