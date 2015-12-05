import sys, datetime, random, time
from os import path, sep, mkdir, walk, remove, rename, stat
from shutil import copy2
from PyQt4 import uic
from PyQt4.QtGui import QApplication, qApp, QFileSystemModel, QMessageBox, QInputDialog, QLineEdit, QDialog, QTreeView, QProgressBar, QStandardItemModel, QStandardItem, QPushButton
from PyQt4.QtCore import Qt
from checkable_dir import CheckableDirModel
from file_types_window import FileTypes
from new_storage_dialog import NewStorage
from restore_dialog import Restore_type
from files_found_dialog import FilesFound
from threading import Thread, Lock
from time import sleep
from checkable_storage import Model as StorageModel
from Crypto.Hash import SHA256
from crcmod import Crc
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
        self.treeViewComputer.setToolTip('Here you can select folders and files that you want to scanning.\n'
                                         'Click on checkbox near name of folder that you want to check.')

        # some staff
        self.system_encoding = sys.getfilesystemencoding()
        self.password = ''
        self.padding = 'eWSxmr3eARFzhuFV'
        self.selected_storage = ''
        self.files_found = {}
        self.files_to_restore = {}
        self.selected_file_types = {}
        self.lock = Lock()
        self.stop = False
        self.threads = []
        self.prev_or_spec = True  # True for restore to previous place, False for specifed
        self.path_to_restore = u''
        self.restore_ok = False
        self.files_found_model = QStandardItemModel
        self.files_found_tree = QTreeView
        self.files_found_ok = False
        self.files_found_cancel = False
        self.files_found_bar = QProgressBar
        self.files_found_ok_enable = QPushButton
        self.category_number_length = {}

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
        self.treeViewStorage.setToolTip('<p><b>Select</b> the storage for backup.</p>'
                                        '<p><b>Check</b> folders or files to restore</p>')
        self.progressBarBackup.setMinimum(0)
        self.progressBarBackup.setValue(0)

        # buttons
        self.scanButton.clicked.connect(self.scan)
        self.fileTypesButton.clicked.connect(self.select_file_types)
        self.backupButtonStorage.clicked.connect(self.backup)
        self.tabWidgetRoot.setCurrentWidget(self.tab_computer)
        self.newStorageButton.clicked.connect(self.add_storage)
        self.restoreButton.clicked.connect(self.restore)



    def scan(self):
        #self.treeViewComputer.setEnabled(False)
        #self.fileTypesButton.setEnabled(False)
        self.files_found = {}
        self.threads = []
        self.stop = False
        if not self.selected_file_types:
            dialog = FileTypes()
            dialog.setModal(True)
            self.selected_file_types, ok = dialog.call()
            if not ok:
                return
        files_found_dialog = FilesFound(self)
        files_found_dialog.setModal(True)
        files_found_dialog.show()
        header_counter = 0
        for element in self.selected_file_types:
            selected = []
            for _type, state in element["Types"].items():
                if state == Qt.Checked:
                    selected.append(_type)
            if selected:
                cat = QStandardItem(element.keys()[0])  # WARNING! it may be unordered
                self.files_found_model.setHorizontalHeaderItem(header_counter, cat)
                self.category_number_length.update({element.keys()[0]: [header_counter, 0]})
                self.files_found_tree.setColumnWidth(header_counter-1, 200)
                header_counter += 1
                for index, state in self.model_computer.checks.items():
                    self.files_found.update({element.keys()[0]: []})
                    print("start tread for %s" % element.keys()[0])
                    th = Thread(target=self.model_computer.exportChecked, args=(self,
                                                                       {index: state},
                                                                       element.keys()[0],
                                                                       selected, self.files_found))
                    th.start()
                    self.threads.append(th)

        status = map(Thread.isAlive, self.threads)
        start_time = time.time()
        while any(status):
            qApp.processEvents()
            status = map(Thread.isAlive, self.threads)
            self.filesFoundLabel.setText("Scanning...")

            if (time.time() - start_time) % 2 == 0:
                if self.files_found:
                    self.lock.acquire()
                    for cat, (num, length) in self.category_number_length.items():
                        files = self.files_found[cat]
                        for i in range(length, len(files)):
                            fileItem = QStandardItem(self.files_found[cat][i].split(sep)[-1])
                            fileItem.setCheckable(True)
                            fileItem.setCheckState(2)
                            fileItem.setToolTip(self.files_found[cat][i])
                            self.files_found_model.invisibleRootItem().setChild(i, num, fileItem)
                        self.category_number_length[cat][1] = len(files)
                    self.lock.release()

        if self.stop:
            self.filesFoundLabel.setText("Scanning was stopped by user")
            self.files_found = {}
            self.threads = []
        else:
            for cat, (num, length) in self.category_number_length.items():
                if self.files_found:
                    files = self.files_found[cat]
                    for i in range(length, len(files)):
                        fileItem = QStandardItem(self.files_found[cat][i].split(sep)[-1])
                        fileItem.setCheckable(True)
                        fileItem.setCheckState(2)
                        fileItem.setToolTip(self.files_found[cat][i])
                        self.files_found_model.invisibleRootItem().setChild(i, num, fileItem)
                    self.category_number_length[cat][1] = len(files)
            self.filesFoundLabel.setText("Scanning finished! Files found %s. Click on the Storage tab" %
                                         sum(len(v) for k, v in self.files_found.items()))
            self.files_found_bar.setMaximum(1)
            self.files_found_bar.setValue(1)
            self.files_found_ok_enable.setEnabled(True)

    def is_exist(self, storage, file_path, category, now_date):
        file_name = file_path.split(sep)[-1]
        for curdir, dirs, files in walk(self.current_dir + storage + sep):
                if curdir.split(sep)[-1] == category and curdir.split(sep)[-2] != now_date:
                    for file in files:
                        if file[:-8] == file_name:
                            checksumm = Crc(0x104c11db7)
                            checksumm.update(file_path)
                            checksumm.update(str(stat(file_path)[-2]))
                            with open(file_path, 'rb') as reader:
                                chunk = reader.read(1024*1024*8)
                                while chunk:
                                    checksumm.update(chunk)
                                    chunk = reader.read(1024*1024*8)

                            if checksumm.hexdigest() == file[-8:]:
                                return True
        return False

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
                if file_path == 'deleted':
                    qApp.processEvents()
                    self.progressBarBackup.setValue(self.progressBarBackup.value()+1)
                    continue
                file_name = file_path.split(sep)[-1]
                if not self.is_exist(warehouse, file_path, category, now_date):
                    checksumm = Crc(0x104c11db7)
                    checksumm.update(file_path)
                    checksumm.update(str(stat(file_path)[-2]))  # modification time
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
                        checksumm.update(part)
                        while part:
                            if len(part) % 16 != 0:
                                part += ' ' * (16 - len(part) % 16)
                            ciphertext = cipher.encrypt(part)
                            writer.write(ciphertext)
                            part = reader.read(chunksize)
                            checksumm.update(part)
                    rename(current_dir+file_name, current_dir+file_name+checksumm.hexdigest())

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
            dialog = QInputDialog()
            dialog.setModal(True)
            key, ok = dialog.getText(self, "Key", "Enter key for <b>%s</b> storage" % storage, mode=QLineEdit.Password)
            if ok:
                try:
                    key = str(key)
                    with open(self.current_dir + storage + sep + "init", 'rb') as f:
                        hash_from_storage = f.read(64)
                        cipter_text = f.read()
                        encryptor = AES.new(key+self.padding[len(key):])
                        plain = encryptor.decrypt(cipter_text)
                        if hash_from_storage == SHA256.new(plain).hexdigest():
                            self.password = key
                            self.encrypt_and_save_to(storage)
                        else:
                            QMessageBox.about(self, "Error", "Incorrect password!")
                except UnicodeError:
                    QMessageBox.about(self, "Error", "Incorrect password!")

        except IndexError:
            if self.selected_storage:
                with open(self.current_dir + self.selected_storage + sep + "init", 'rb') as f:
                        hash_from_storage = f.read(64)
                        cipter_text = f.read()
                        encryptor = AES.new(self.password+self.padding[len(self.password):])
                        plain = encryptor.decrypt(cipter_text)
                        if hash_from_storage == SHA256.new(plain).hexdigest():
                            self.password = key
                            self.encrypt_and_save_to(self.selected_storage)
                        else:
                            QMessageBox.about(self, "Error", "Incorrect password!")
            else:
                QMessageBox.about(self, "Error", "Select the storage before creating backup!")
                self.tabWidgetRoot.setCurrentWidget(self.tab_storage)
        except WindowsError:
            QMessageBox.about(self, "Error", "Too little time for previous backup!\nWait a minute, please.")

    def restore(self):
        self.progressBarBackup.setMinimum(0)
        self.progressBarBackup.setMaximum(0)
        self.restoreButton.setEnabled(False)
        self.threads = []
        self.files_to_restore = {}
        for index, state in self.model_storage.checks.items():
            th = Thread(target=self.model_storage.exportChecked, args=(self.lock, {index: state}, self.files_to_restore))
            th.start()
            self.threads.append(th)

        status = map(Thread.isAlive, self.threads)

        while any(status):
            qApp.processEvents()
            status = map(Thread.isAlive, self.threads)

        self.progressBarBackup.setMaximum(100)
        self.progressBarBackup.setValue(100)
        if self.files_to_restore:
            files_count = sum(len(f) for cat in self.files_to_restore.values() for date in cat.values() for f in date.values()[0])
            self.progressBarBackup.setMaximum(files_count)
            self.progressBarBackup.setValue(0)
            dialog = Restore_type(self)
            dialog.setModal(True)
            self.prev_or_spec, self.path_to_restore, ok = dialog.call(self)
            print(self.files_to_restore)
            if ok:
                for storage, categories in self.files_to_restore.items():
                    dialog = QInputDialog()
                    dialog.setModal(True)
                    key, ok = dialog.getText(self, "Key", "Enter key for <b>%s</b> storage" % storage,
                                                   mode=QLineEdit.Password)
                    if ok:
                        try:
                            key = str(key)
                            with open(self.current_dir + storage + sep + "init", 'rb') as f:
                                hash_from_storage = f.read(64)
                                cipter_text = f.read()
                                encryptor = AES.new(key+self.padding[len(key):])
                                plain = encryptor.decrypt(cipter_text)
                                if hash_from_storage == SHA256.new(plain).hexdigest():
                                    for cat, backups in categories.items():
                                        sorted_by_date = sorted(backups.keys(), key=lambda x: x)
                                        for backup in sorted_by_date:
                                            for fn in backups[backup]:
                                                path_to_file = self.current_dir+storage+sep+backup+sep+cat+sep+fn
                                                self.decrypt_and_save(path_to_file, key,
                                                                      new_path=self.path_to_restore+sep+cat if not self.prev_or_spec else '')
                                                self.progressBarBackup.setValue(self.progressBarBackup.value()+1)
                                    self.progressBarBackup.setValue(self.progressBarBackup.maximum())
                                else:
                                    QMessageBox.about(self, "Error", "Incorrect password!")
                        except UnicodeError:
                            QMessageBox.about(self, "Error", "Incorrect password!")
        else:
            QMessageBox.about(self, "Error", "Select the storage/backup/file before restoring!")
        self.restoreButton.setEnabled(True)

    def decrypt_and_save(self, path_to_file, key, new_path):
        with open(path_to_file, 'rb') as ciphered:
                origsize = unpack('<Q', ciphered.read(calcsize('Q')))[0]
                iv = ciphered.read(16)
                path_to_save = ciphered.read(unpack('<B', ciphered.read(1))[0])
                if new_path:
                    if not path.exists(new_path):
                        mkdir(new_path)
                    file_name = path_to_file.split(sep)[-1][:-8]
                    path_to_save = new_path+sep+file_name
                    if path.exists(path_to_save):
                        path_to_save = new_path+sep+path_to_file.split(sep)[-1]
                else:
                    p = ''
                    for dir in path_to_save.split(sep)[:-1]:
                        p += dir + sep
                        if not path.exists(p):
                            mkdir(p)
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
        dialog = FileTypes()
        dialog.setModal(True)
        types, ok = dialog.call()
        if ok:
            self.selected_file_types = types


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())