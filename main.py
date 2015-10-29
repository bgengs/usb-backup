#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
from PyQt4 import uic
from PyQt4.QtGui import QStandardItemModel, QDirModel, QFileDialog, QStandardItem, QApplication
from PyQt4.QtCore import Qt, QFileInfo, QObject, SIGNAL, QCoreApplication

class CheckableFileTypes(QStandardItemModel):
    def __init__(self, parent=None):
        super(CheckableFileTypes, self).__init__(parent)
        self.checks = {}
        self.root = self.invisibleRootItem()

    def appendRow(self, args):
        return QStandardItemModel.appendRow(self, args)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)

        return QStandardItemModel.data(self, index, role)

    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return Qt.Unchecked

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled

    def setData(self, index, value, role):

        if role == Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            #for i, v in self.checks.items():
            #    if are_parent_and_child(index, i):
            #        self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True

        return QDirModel.setData(self, index, value, role)

    def exportChecked(self):
        indexes = []
        for index in self.checks.keys():
            if self.checks[index] == Qt.Checked:
                indexes.append(index)

        return indexes

def are_parent_and_child(parent, child):
    while child.isValid():
        if child == parent:
            return True
        child = child.parent()
    return False

class CheckableDirModel(QDirModel):
    def __init__(self, parent=None):
        QDirModel.__init__(self, None)
        self.checks = {}

    def data(self, index, role=Qt.DisplayRole):
        #print("data")
        if role == Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return QDirModel.data(self, index, role)

    def flags(self, index):
        return QDirModel.flags(self, index) | Qt.ItemIsUserCheckable

    def checkState(self, index):

        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return Qt.Unchecked

    def setData(self, index, value, role):
        print("setdata")
        if role == Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            for i, v in self.checks.items():
                if are_parent_and_child(index, i):
                    self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True

        return QDirModel.setData(self, index, value, role)

    def exportChecked(self, acceptedSuffix=['jpg', 'png', 'bmp']):
        selection = []
        for index in self.checks.keys():
            if self.checks[index] == Qt.Checked:
                if os.path.isfile(unicode(self.filePath(index))):
                    #if QtCore.QFileInfo(unicode(self.filePath(index)).split(os.sep)[-1]).completeSuffix().toLower() in acceptedSuffix:
                    selection.append(unicode(self.filePath(index)))
                else:
                    for path, dirs, files in os.walk(unicode(self.filePath(index))):
                        for filename in files:
                            if QFileInfo(filename).completeSuffix().toLower() in acceptedSuffix:
                                if self.checkState(self.index(os.path.join(path, filename))) == Qt.Checked:
                                    try:
                                        selection.append(os.path.join(path, filename))
                                    except:
                                        pass
        return selection

base, form = uic.loadUiType("design"+os.sep+"secure_usb_backup.ui")
class MainWindow(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.resize(600, 500)
        self.model = CheckableDirModel()
        self.treeViewComputer.setModel(self.model)
        self.treeViewComputer.setAnimated(False)
        self.treeViewComputer.setIndentation(10)
        self.treeViewComputer.setSortingEnabled(True)
        self.treeViewComputer.setWindowTitle("Dir View")
        self.treeViewComputer.setColumnWidth(0, 200)
        self.treeViewComputer.setColumnWidth(1, 80)
        self.treeViewComputer.setColumnWidth(2, 80)

        self.foldersButton.clicked.connect(self.select_folder)
        self.tabWidgetRoot.setCurrentWidget(self.tab_computer)

        self.files = []
        self.selected_file_types = {}
        self.scanButton.clicked.connect(self.scan)

        self.fileTypesButton.clicked.connect(self.select_file_types)

    def scan(self):
        print(self.selected_file_types)

    def select_file_types(self):
        dialog = FileTypes(self)
        dialog.show()

    def select_folder(self, folder=None):
        if not folder:
            folder = unicode(QFileDialog.getExistingDirectory(self, "Select Directory"))
            #self.add_to_tree(folder)


base2, form2 = uic.loadUiType("design"+os.sep+"file_types_dialog.ui")

class FileTypes(base2, form2):
    def __init__(self, parent=None):
        super(base2, self).__init__(parent)
        self.setupUi(self)
        self.categories = {"Develop": ["py", "rb", "h", "html", "css"],
                           "Image": ["jpg", "jpeg", "bmp", "gif", "png"],
                           "Movies": ["avi", "mkv", "mov", "mp4"],
                           "Documents": ["doc", "docx", "xls", "xlsx", "ppt", "pptx"],
                           "Music": ["mp3", "wav"]}
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.setHorizontalHeaderItem(0, QStandardItem(""))
        parent.selected_file_types = {12:12}
        QObject.connect(self.okCancelBox, SIGNAL("accepted()"), lambda parent_window=parent: self.submit_file_types(parent_window))
        QObject.connect(self.okCancelBox, SIGNAL("rejected()"), self.close)

        #putting
        for cat, types in self.categories.items():
            catItem = QStandardItem(cat)
            catItem.setCheckable(True)
            for type in types:
                typeItem = QStandardItem(type)
                typeItem.setCheckable(True)
                catItem.appendRow(typeItem)
            self.model.appendRow(catItem)
        self.treeView.setModel(self.model)

    def quit(self, event):
        self.close()

    def on_item_changed(self, item):
        if item.checkState() == Qt.Checked:
            if item.hasChildren():
                for row in range(item.rowCount()):
                    item.child(row).setCheckState(Qt.Checked)
            else:
                item.parent().setCheckState(Qt.PartiallyChecked)

        elif item.checkState() == Qt.Unchecked:
            if item.hasChildren():
                for row in range(item.rowCount()):
                    item.child(row).setCheckState(Qt.Unchecked)
            else:
                children = range(item.parent().rowCount())
                children.pop(item.index().row())
                for row in children:
                    if item.parent().child(row).checkState():
                        return
                item.parent().setCheckState(Qt.Unchecked)


    def submit_file_types(self, parent_window):
        checked = {}
        root = self.model.invisibleRootItem()

        for num_cat in range(root.rowCount()):
            category = root.child(num_cat, 0)
            for num_type in range(category.rowCount()):
                if category.child(num_type, 0).checkState() == Qt.Checked:
                    try:
                        checked[category.text()].append(category.child(num_type, 0).text())
                    except KeyError:
                        checked.update({category.text(): [category.child(num_type, 0).text()]})
        parent_window.selected_file_types = checked
        self.close()

    def get_selected_file_types(self):
        return self.selected_file_types

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
