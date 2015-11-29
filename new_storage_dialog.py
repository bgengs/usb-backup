from PyQt4 import uic
from PyQt4.QtGui import QLineEdit, QLabel, QPalette, QItemSelectionModel
from PyQt4.QtCore import Qt, QObject, SIGNAL, QRect
from os import sep, path, mkdir, walk
from Crypto.Hash import SHA256
from string import printable

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
                    open(current_dir+sep+"hash",'w').write(SHA256.new(password + parent.padding[len(password):]).hexdigest())
                    parent.password = password
                    parent.selected_storage = storage
                    index = parent.model_storage.index(current_dir)
                    #parent.treeViewStorage.setSelection(index, QItemSelectionModel.NoUpdate)
                    parent.treeViewStorage.setCurrentIndex(index)
                    self.close()
            except UnicodeError:
                self.errorLabel.setText("Password or Name has unacceptable symbols!")
