import sys, datetime, random
from os import path, sep, mkdir, walk, remove
from shutil import copy2
from PyQt4 import uic
from PyQt4.QtGui import QApplication, qApp, QFileSystemModel, QMessageBox, QInputDialog, QLineEdit, QDialog, QTreeView, QProgressBar
from PyQt4.QtCore import Qt
from checkable_dir import CheckableDirModel
from file_types_window import FileTypes
from new_storage_dialog import NewStorage
from restore_dialog import Restore_type
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
        self.files_found = {}
        self.files_to_restore = {}
        self.selected_file_types = {}
        self.lock = Lock()
        self.threads = []
        self.prev_or_spec = True  # True for restore to previous place, False for specifed
        self.path_to_restore = u''
        self.restore_ok = False

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
        self.progressBarBackup.setMinimum(0)
        self.progressBarBackup.setValue(0)

        # buttons
        self.scanButton.clicked.connect(self.scan)
        self.fileTypesButton.clicked.connect(self.select_file_types)
        self.backupButtonComp.clicked.connect(self.backup)
        self.backupButtonStorage.clicked.connect(self.backup)
        self.tabWidgetRoot.setCurrentWidget(self.tab_computer)
        self.newStorageButton.clicked.connect(self.add_storage)
        self.helpButtonComputer.clicked.connect(self.help)
        self.restoreButton.clicked.connect(self.restore)

    def help(self):
        print(self.password)

    def scan(self):
        #self.treeViewComputer.setEnabled(False)
        self.backupButtonComp.setEnabled(False)
        #self.fileTypesButton.setEnabled(False)
        self.files_found = {}
        self.threads = []
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
                    self.files_found.update({element.keys()[0]: []})
                    print("start tread for %s" % element.keys()[0])
                    th = Thread(target=self.model_computer.exportChecked, args=(self.lock,
                                                                       {index: state},
                                                                       element.keys()[0],
                                                                       selected, self.files_found))
                    th.start()
                    self.threads.append(th)

        status = map(Thread.isAlive, self.threads)

        while any(status):
            qApp.processEvents()
            status = map(Thread.isAlive, self.threads)
            self.filesFoundLabel.setText("Scaning...")

        self.filesFoundLabel.setText("Scaning finished! Files found %s" % sum(len(v) for k, v in self.files_found.items()))

        #self.treeViewComputer.setEnabled(True)
        self.backupButtonComp.setEnabled(True)
        #self.fileTypesButton.setEnabled(True)

    def is_exist(self, storage, file_path, category):  # in storage
        file_name = file_path.split(sep)[-1]
        for curdir, dirs, files in walk(self.current_dir + storage + sep):
            if curdir.split(sep)[-1] == category:
                for file in files:
                    if file == file_name:
                        sha_existed = SHA256.new()
                        sha_found = SHA256.new()
                        with open(curdir+sep+file, 'rb') as ciphered, open(file_path, 'rb') as found:
                            origsize = unpack('<Q', ciphered.read(calcsize('Q')))[0]
                            current_len = 0
                            iv = ciphered.read(16)
                            saved_file_path = ciphered.read(unpack('<B', ciphered.read(1))[0])
                            if saved_file_path != file_path:
                                continue
                            decryptor = AES.new(self.password+self.padding[len(self.password):], AES.MODE_CBC, iv)
                            chunksize = 64*1024*16

                            pure_chunk = found.read(chunksize)
                            crypt_chunk = ciphered.read(chunksize)
                            #print('existed', curdir+sep+file)
                            #print('foubd', file_path)
                            #print('pure', len(pure_chunk))
                            #print('crypt', len(crypt_chunk))
                            #print('orgsize', origsize)
                            while crypt_chunk:
                                plain = decryptor.decrypt(crypt_chunk)
                                current_len += len(plain)
                                if current_len > origsize:
                                    trunk = current_len-origsize
                                    plain = plain[:-trunk]
                                    print('trunk', len(plain))
                                sha_existed.update(plain)
                                sha_found.update(pure_chunk)
                                if sha_existed.hexdigest() != sha_found.hexdigest():
                                    break
                                crypt_chunk = ciphered.read(chunksize)
                                pure_chunk = found.read(chunksize)
                        return True, curdir+sep+file
        return False, ''

    def encrypt_and_save_to(self, warehouse):
        files_count = sum(len(f) for f in self.files_found.values())
        self.progressBarBackup.setMaximum(files_count)
        self.progressBarBackup.setValue(0)
        now_date = datetime.datetime.now().strftime('Backup_%m-%d-%y_%H-%M')
        mkdir(self.current_dir + warehouse + sep + now_date + sep)
        for category, files in self.files_found.items():
            current_dir = self.current_dir + warehouse + sep + now_date + sep + category + sep
            if not path.exists(current_dir):
                mkdir(current_dir)
            for file_path in files:
                file_name = file_path.split(sep)[-1]
                exist = self.is_exist(warehouse, file_path, category)
                if not exist[0]:
                    with open(file_path, 'rb') as reader, open(current_dir+file_name, 'wb') as writer:
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
                        writer.write(exist[1])
                qApp.processEvents()
                self.progressBarBackup.setValue(self.progressBarBackup.value()+1)
        self.progressBarBackup.setValue(self.progressBarBackup.maximum())

    def backup(self):
        try:
            selected_index = self.treeViewStorage.selectedIndexes()[0]
            selected_path = self.model_storage.filePath(selected_index).split('/')[::-1]
            storage = ''
            for i, dir in enumerate(selected_path):
                if dir == "Backups":
                    storage = str(selected_path[i-1])

            hash_from_storage = open(self.current_dir + storage + sep + "hash", 'r').read()
            hash_from_user = SHA256.new(self.password+self.padding[len(self.password):]).hexdigest()
            if self.selected_storage == storage and hash_from_user == hash_from_storage:
                print("when selected and already backuped", self.password)
                self.encrypt_and_save_to(storage)
            else:
                key, ok = QInputDialog.getText(self, "Key", "Enter key for <b>%s</b> storage" % storage,
                                               mode=QLineEdit.Password)
                if ok:
                    try:
                        key = str(key)
                    except UnicodeError:
                        QMessageBox.about(self, "Error", "Incorrect password!")
                    hash_from_user = SHA256.new(key+self.padding[len(key):]).hexdigest()
                    self.password = key
                    if hash_from_user == hash_from_storage:
                        print("when selected", self.password)
                        self.encrypt_and_save_to(storage)
                    else:
                        QMessageBox.about(self, "Error", "Incorrect password!")

        except IndexError:
            if self.selected_storage:
                hash_from_storage = open(self.current_dir + self.selected_storage + sep + "hash", 'r').read()
                hash_from_user = SHA256.new(self.password+self.padding[len(self.password):]).hexdigest()
                if hash_from_user == hash_from_storage:
                    print("when new created", self.password)
                    self.encrypt_and_save_to(self.selected_storage)
            else:
                QMessageBox.about(self, "Error", "Select the storage before creating backup!")
                self.tabWidgetRoot.setCurrentWidget(self.tab_storage)
        except WindowsError:
            QMessageBox.about(self, "Error", "Too little time for previous backup!\nWait a minute, please.")

    def restore(self):
        self.progressBarBackup.setMinimum(0)
        self.progressBarBackup.setMaximum(0)
        self.threads = []
        self.files_to_restore = {}
        #print(self.treeViewStorage)
        for index, state in self.model_storage.checks.items():
            th = Thread(target=self.model_storage.exportChecked, args=(self.lock, {index: state}, self.files_to_restore))
            th.start()
            self.threads.append(th)

        status = map(Thread.isAlive, self.threads)

        while any(status):
            qApp.processEvents()
            status = map(Thread.isAlive, self.threads)

        self.progressBarBackup.setMaximum(100)
        if self.files_to_restore:
            dialog = Restore_type(self)
            dialog.setModal(True)
            self.prev_or_spec, self.path_to_restore, ok = dialog.call(self)

            if ok:
                for storage, categories in self.files_to_restore.items():
                    hash_from_storage = open(self.current_dir + storage + sep + "hash", 'r').read()
                    key, ok = QInputDialog.getText(self, "Key", "Enter key for <b>%s</b> storage" % storage,
                                                   mode=QLineEdit.Password)
                    if ok:
                        try:
                            key = str(key)
                        except UnicodeError:
                            QMessageBox.about(self, "Error", "Incorrect password!")
                        hash_from_user = SHA256.new(key+self.padding[len(key):]).hexdigest()
                        if hash_from_user == hash_from_storage:
                            for cat, backups in categories.items():
                                sorted_by_date = sorted(backups.keys(), key=lambda x: x, reverse=True)
                                for backup in sorted_by_date:
                                    for fn in backups[backup]:
                                        path_to_file = self.current_dir+storage+sep+backup+sep+cat+sep+fn
                                        if fn.split('.')[-1] == 'link':
                                            path_to_file = open(self.current_dir+storage+sep+backup+sep+cat+sep+fn, 'r').read()
                                        self.decrypt_and_save(path_to_file, key, new_path=self.path_to_restore if not self.prev_or_spec else '')
                        else:
                            QMessageBox.about(self, "Error", "Incorrect password!")
        else:
            QMessageBox.about(self, "Error", "Select the storage/backup/file before restoring!")

    def decrypt_and_save(self, path_to_file, key, new_path):
        with open(path_to_file, 'rb') as ciphered:
                origsize = unpack('<Q', ciphered.read(calcsize('Q')))[0]
                iv = ciphered.read(16)
                path_to_save = ciphered.read(unpack('<B', ciphered.read(1))[0])
                if new_path:
                    path_to_save = new_path+sep+path_to_file.split(sep)[-1]
                if not path.exists(path_to_save):
                    decryptor = AES.new(key+self.padding[len(key):], AES.MODE_CBC, iv)
                    chunksize = 24*1024
                    with open(path_to_save, 'wb') as outfile:
                        chunk = ciphered.read(chunksize)
                        while chunk:
                            outfile.write(decryptor.decrypt(chunk))
                            chunk = ciphered.read(chunksize)
                        outfile.truncate(origsize)

    def add_storage(self):
        dialog = NewStorage(self)
        dialog.setModal(True)
        dialog.show()

    def select_file_types(self):
        dialog = FileTypes(self)
        dialog.setModal(True)
        dialog.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

            #print(str(self.model_storage.filePath(selected_index).split('/')))
            #warehouse = str(self.model_storage.filePath(selected_index).split('/')[-1])