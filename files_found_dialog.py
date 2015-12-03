from PyQt4.QtGui import QStandardItemModel, QStandardItem, QInputDialog, QMenu, QApplication, QTreeView, QDialog
from PyQt4.QtCore import Qt, QObject, SIGNAL, QVariant
from PyQt4 import uic
from os import sep
import sys

base, form = uic.loadUiType("design"+sep+"files_found_dialog.ui")
class FilesFound(base, form):
    def __init__(self, parent_win=None):
        super(base, self).__init__(parent_win)
        self.setupUi(self)
        self.parent = parent_win

        self.treeViewFound.setIndentation(0)
        self.model = QStandardItemModel()
        #QObject.connect(self.model, SIGNAL("itemChanged(QStandardItem*)"), lambda parent=parent_win: self.on_item_changed(parent))
        self.model.itemChanged.connect(self.on_item_changed)
        self.treeViewFound.setModel(self.model)
        parent_win.files_found_model = self.model
        parent_win.files_found_tree = self.treeViewFound
        self.okButton.setEnabled(False)
        QObject.connect(self.okButton, SIGNAL("clicked()"), lambda parent=parent_win: self.ok(parent))
        QObject.connect(self.cancelButton, SIGNAL("clicked()"), lambda parent=parent_win: self.cancel(parent))
        self.progressBar.setMaximum(0)
        self.progressBar.setMinimum(0)
        parent_win.files_found_bar = self.progressBar
        parent_win.files_found_ok_enable = self.okButton

    def ok(self, parent):
        parent.files_found_ok = True
        self.close()

    def cancel(self, parent):
        parent.stop = True
        self.close()

    def on_item_changed(self, item):
        cat = unicode(self.model.headerData(item.column(), Qt.Horizontal).toString())
        if item.checkState() == 2 and unicode(item.toolTip()) != self.parent.files_found[cat][item.row()]:
            self.parent.files_found[cat][item.row()] = unicode(item.toolTip())
        elif item.checkState() == 0:
            self.parent.files_found[cat][item.row()] = 'deleted'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilesFound()
    ex.exec_()