from PyQt4 import uic
from PyQt4.QtGui import QLineEdit, QLabel, QPalette, QItemSelectionModel, QRadioButton, QFileDialog, QAction, QDialog
from PyQt4.QtCore import Qt, QObject, SIGNAL, QRect, SLOT
from os import sep

base, form = uic.loadUiType("design"+sep+"restore_dialog.ui")
class Restore_type(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.prev_or_spec = True  # True for previous, False for specifed
        self.radioButtonPrev.toggled.connect(self.previous)
        self.radioButtonPrev.setChecked(True)
        self.radioButtonSpec.toggled.connect(self.specify)
        self.browseButton.clicked.connect(self.browse)
        self.selected_path = u''
        #self.cancelButton.clicked.connect(self.close)
        #self.okButton.clicked.connect(self.ok)
        #QObject.connect(self.okButton, SIGNAL("clicked()"), lambda parent=parent: self.ok(parent))
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def previous(self, enabled):
        if enabled:
            self.browseButton.setEnabled(False)
            self.prev_or_spec = True
            self.labelPath.setText('')
            self.selected_path = u''

    def specify(self, enabled):
        if enabled:
            self.browseButton.setEnabled(True)
            self.prev_or_spec = False

    def current_state(self):
        return self.prev_or_spec, self.selected_path

    def browse(self):
        self.selected_path = unicode(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.labelPath.setText(u'Restore to '+self.selected_path)

    @staticmethod
    def call(parent=None):
        dialog = Restore_type(parent)
        result = dialog.exec_()
        prev_or_spec, path = dialog.current_state()
        return(prev_or_spec, path, result == QDialog.Accepted)