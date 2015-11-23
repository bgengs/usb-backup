import sys, datetime, random
from os import path, sep, mkdir, walk, remove
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
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from struct import pack, unpack, calcsize


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
        self.padding = 'eWSxmr3eARFzhuFV'
        self.selected_storage = ''
        self.files = {}
        self.selected_file_types = {}
        self.lock = Lock()
        self.threads = []

        self.model_storage = StorageModel()
        if not path.exists(path.dirname(path.abspath(__file__)) + sep + "Backups"):
            mkdir(path.dirname(path.abspath(__file__)) + sep + "Backups")
        self.current_dir = path.dirname(path.abspath(__file__)).decode(self.system_encoding) + sep + "Backups" + sep
        self.model_storage.setRootPath(path.dirname(path.abspath(__file__)).decode(self.system_encoding) + sep + "Backups")
        self.treeViewStorage.setModel(self.model_storage)
        self.treeViewStorage.setRootIndex(self.model_storage.index(self.model_storage.rootPath()))
        self.treeViewStorage.setIndentation(10)
        self.treeViewStorage.setSortingEnabled(True)
        self.treeViewStorage.setColumnWidth(0, 200)
        self.treeViewStorage.setColumnWidth(1, 80)
        self.treeViewStorage.setColumnWidth(2, 80)
        #self.treeViewStorage.setItemsExpandable(False)
        """
        (_, storages, _) = next(walk(self.current_dir))
        for storage in storages:
            self.treeViewStorage.setExpanded(self.model_storage.index(self.current_dir + storage), False)
            """

        #self.treeViewStorage(self.model_storage.index(self.current_dir + "AlexeyPC"), False)
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
        #self.treeViewComputer.setEnabled(False)
        self.backupButtonComp.setEnabled(False)
        #self.fileTypesButton.setEnabled(False)
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
        '''
        while any(status):
            status = map(Thread.isAlive, self.threads)
            sleep(.5)
            self.filesFoundLabel.setText("Scaning.")
            sleep(.5)
            self.filesFoundLabel.setText("Scaning..")
            sleep(.5)
            self.filesFoundLabel.setText("Scaning...")
        '''
        self.filesFoundLabel.setText("Scaning finished! Files found %s" % sum(len(v) for k, v in self.files.items()))

        #self.treeViewComputer.setEnabled(True)
        self.backupButtonComp.setEnabled(True)
        #self.fileTypesButton.setEnabled(True)

    def is_exist(self, warehouse, file_path, category): # in warehouse
        file_name = file_path.split(sep)[-1]
        return_value = False
        checked = False
        for curdir, dirs, files in walk(self.current_dir + warehouse + sep):
            if curdir.split(sep)[-1] == category:
                for file in files:
                    if file == file_name:
                        decrypted = self.decrypt(curdir+sep+file)
                        with open(decrypted, 'r') as dec, open(file_path, 'r') as new:
                            existed = SHA256.new(dec.read())
                            found = SHA256.new(new.read())
                            if existed.hexdigest() == found.hexdigest():
                                return_value = True
                            checked = True
        if checked:
            remove(decrypted)
        return return_value

    def decrypt(self, file_path):
        with open(file_path, 'r') as ciphered:
            origsize = unpack('<Q', ciphered.read(calcsize('Q')))[0]
            iv = ciphered.read(16)
            saved_file_path = ciphered.read(unpack('<B', ciphered.read(1))[0])
            decryptor = AES.new(self.password+self.padding[len(self.password):], AES.MODE_CBC, iv)
            chunksize = 24*1024
            with open(file_path+'.dec', 'wb') as outfile:
                chunk = ciphered.read(chunksize)
                while chunk:
                    outfile.write(decryptor.decrypt(chunk))
                    chunk = ciphered.read(chunksize)
                outfile.truncate(origsize)
        return file_path+'.dec'

    def encrypt_and_save_to(self, warehouse):
        now_date = datetime.datetime.now().strftime('Backup_%m-%d-%y_%H-%M')
        mkdir(self.current_dir + warehouse + sep + now_date + sep)
        for category, files in self.files.items():
            current_dir = self.current_dir + warehouse + sep + now_date + sep + category + sep
            if not path.exists(current_dir):
                mkdir(current_dir)
            for file_path in files:
                file_name = file_path.split(sep)[-1]
                if not self.is_exist(warehouse, file_path, category):
                    with open(file_path, 'rb') as reader, open(current_dir+file_name, 'ab') as writer:
                        chunksize=64*1024*16
                        iv = ''.join(chr(random.randint(0, 0xFF)) for _ in range(16))
                        cipher = AES.new(self.password+self.padding[len(self.password):], AES.MODE_CBC, iv)
                        filesize = path.getsize(file_path)

                        writer.write(pack('<Q', filesize))
                        writer.write(iv)
                        writer.write(pack('<B', len(file_path)))
                        writer.write(file_path)

                        part = reader.read(chunksize)
                        while part:
                            if len(part) % 16 != 0:
                                part += ' ' * (16 - len(part) % 16)
                            ciphertext = cipher.encrypt(part)
                            writer.write(ciphertext)
                            part = reader.read(chunksize)
                else:
                    with open(current_dir+file_name+'.link', 'w') as writer:
                        writer.write(file_path)

    def backup(self):
        try:
            selected_index = self.treeViewStorage.selectedIndexes()[0]
            selected_path = self.model_storage.filePath(selected_index).split('/')[::-1]
            warehouse = ''
            for i, dir in enumerate(selected_path):
                if dir == "Backups":
                    warehouse = str(selected_path[i-1])

            hash_from_storage = open(self.current_dir + warehouse + sep + "hash", 'r').read()
            hash_from_user = SHA256.new(self.password+self.padding[len(self.password):]).hexdigest()
            if self.selected_storage == warehouse and hash_from_user == hash_from_storage:
                self.encrypt_and_save_to(warehouse)

            else:
                key, ok = QInputDialog.getText(self, "Key", "Enter key for <b>%s</b> storage" % warehouse,
                                               mode=QLineEdit.Password)
                if ok:
                    hash_from_user = SHA256.new(key+self.padding[len(key):]).hexdigest()
                    if hash_from_user == hash_from_storage:
                        self.encrypt_and_save_to(warehouse)
                    else:
                        QMessageBox.about(self, "Error", "Incorrect password!")

        except IndexError:
            if self.selected_storage:
                hash_from_storage = open(self.current_dir + self.selected_storage + sep + "hash", 'r').read()
                hash_from_user = SHA256.new(self.password+self.padding[len(self.password):]).hexdigest()
                if hash_from_user == hash_from_storage:
                    self.encrypt_and_save_to(self.selected_storage)
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

            #print(str(self.model_storage.filePath(selected_index).split('/')))
            #warehouse = str(self.model_storage.filePath(selected_index).split('/')[-1])