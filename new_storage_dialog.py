from PyQt4 import uic
from PyQt4.QtGui import QLineEdit, QLabel, QPalette, QItemSelectionModel
from PyQt4.QtCore import Qt, QObject, SIGNAL, QRect
from os import sep, path, mkdir
from Crypto.Hash import SHA256

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
            current_dir = parent.current_dir + str(self.storageNameLine.text())
            mkdir(current_dir)
            password = self.passLine.text()+parent.padding[len(self.passLine.text()):]
            open(current_dir + sep + "hash", 'w').write(SHA256.new(password).hexdigest())
            parent.password = self.passLine.text()
            parent.selected_storage = str(self.storageNameLine.text())
            index = parent.model_storage.index(current_dir)
            #parent.treeViewStorage.setSelection(index, QItemSelectionModel.NoUpdate)
            parent.treeViewStorage.setCurrentIndex(index)
            self.close()