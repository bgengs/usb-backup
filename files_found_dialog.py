from PyQt4.QtGui import QStandardItemModel, QMessageBox, QItemSelectionModel, QItemSelection, QStandardItem, QInputDialog, QMenu, QApplication, QTreeView, QDialog
from PyQt4.QtCore import Qt, QObject, SIGNAL, QVariant
from PyQt4 import uic
from os import sep
import sys, subprocess, platform

class MyModel(QStandardItemModel ):
    def __init__(self, parent=None):
        super(MyModel, self).__init__(parent)


base, form = uic.loadUiType("design"+sep+"files_found_dialog.ui")
class FilesFound(base, form):
    def __init__(self, parent_win=None):
        super(base, self).__init__(parent_win)
        self.setupUi(self)
        self.parent = parent_win

        self.treeViewFound.setIndentation(0)
        self.treeViewFound.setToolTip("Here you can see files that was found on your computer.\n"
                                      "If you don't want backup it - just uncheck it.\n"
                                      "Right click on file to show file in Explorer")
        self.model = QStandardItemModel()
        #self.model = MyModel(self)
        #self.selModel = QItemSelectionModel(self.model)
        #QObject.connect(self.model, SIGNAL("itemChanged(QStandardItem*)"), lambda parent=parent_win: self.on_item_changed(parent))
        self.model.itemChanged.connect(self.on_item_changed)

        self.treeViewFound.setModel(self.model)
        #self.treeViewFound.setSelectionModel(self.selModel)
        #self.treeViewFound.selectionModel().selectionChanged.connect(self.on_item_changed)
        parent_win.files_found_model = self.model
        parent_win.files_found_tree = self.treeViewFound
        self.okButton.setEnabled(False)
        QObject.connect(self.okButton, SIGNAL("clicked()"), lambda parent=parent_win: self.ok(parent))
        QObject.connect(self.cancelButton, SIGNAL("clicked()"), lambda parent=parent_win: self.cancel(parent))
        self.progressBar.setMaximum(0)
        self.progressBar.setMinimum(0)
        parent_win.files_found_bar = self.progressBar
        parent_win.files_found_ok_enable = self.okButton
        self.treeViewFound.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeViewFound.customContextMenuRequested.connect(self.open_menu)

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

    def open_menu(self, position):
        index = self.treeViewFound.selectedIndexes()[0]
        path = self.model.itemFromIndex(index).toolTip()
        menu = QMenu()
        menu.addAction(self.tr("Show in Explorer"), lambda x=path: self.path_to_buffer(x))
        menu.exec_(self.treeViewFound.viewport().mapToGlobal(position))

    def path_to_buffer(self, path):
        if platform.system() == 'Windows':
            subprocess.Popen('explorer "%s"' % (sep.join(str(x) for x in path.split(sep)[:-1])))
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', sep.join(str(x) for x in path.split(sep)[:-1])])
        elif platform.system() == 'Linux':
            subprocess.Popen(['xdg-open', sep.join(str(x) for x in path.split(sep)[:-1])])
        else:
            QMessageBox.about(self, "Error", "OS is not recognized. Send me email about your problem. peretsmobil@gmail.com ")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilesFound()
    ex.exec_()