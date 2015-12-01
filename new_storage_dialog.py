from PyQt4 import uic
from PyQt4.QtGui import QLineEdit, QLabel, QPalette, QItemSelectionModel
from PyQt4.QtCore import Qt, QObject, SIGNAL, QRect
from os import sep, path, mkdir, walk
from Crypto.Hash import SHA256
from random import getrandbits
from Crypto.Cipher import AES


base, form = uic.loadUiType("design"+sep+"new_storage_dialog.ui")
class NewStorage(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)

        self.cancelButton.clicked.connect(self.close)
        QObject.connect(self.okButton, SIGNAL("clicked()"), lambda parent=parent: self.ok(parent))
        self.passLine.setEchoMode(QLineEdit.Password)
        self.confirmLine.setEchoMode(QLineEdit.Password)

    def ok(self, parent):
        palette = QPalette()
        palette.setColor(QPalette.Foreground, Qt.red)
        self.errorLabel.setPalette(palette)
        if any([not self.storageNameLine.text(), not self.passLine.text(), not self.confirmLine.text()]):
            self.errorLabel.setText("All fields are required!")
        #elif len(self.passLine.text()) < 8 or len(self.passLine.text()) > 16:
        #    self.errorLabel.setText("Password must contain 8-16 characters!")
        elif any(ch in self.storageNameLine.text() for ch in r'*|\:"<>?/'):  #TODO: to check name for linux and mac
            self.errorLabel.setText("Name has unacceptable symbols!")
        elif self.passLine.text() != self.confirmLine.text():
            self.errorLabel.setText("Password mismatch!")
        else:
            try:
                password = str(self.passLine.text())
                storage = str(self.storageNameLine.text())
                if storage in next(walk(parent.current_dir))[1]:
                    self.errorLabel.setText("Name already exist!")
                else:
                    current_dir = parent.current_dir + storage
                    mkdir(current_dir)
                    hash = SHA256.new()
                    cipher = AES.new(password+parent.padding[len(password):])
                    cipher_text = ''
                    for i in range(10*1024):
                        new_part = reduce(lambda x, y: x+y, [chr(getrandbits(8)) for _ in range(16)])
                        hash.update(new_part)
                        cipher_text += cipher.encrypt(new_part)

                    open(current_dir+sep+"init", 'wb').write(hash.hexdigest()+cipher_text)

                    parent.password = password
                    parent.selected_storage = storage
                    index = parent.model_storage.index(current_dir)
                    parent.treeViewStorage.setCurrentIndex(index)
                    self.close()
            except UnicodeError:
                self.errorLabel.setText("Password or Name has unacceptable symbols!")
