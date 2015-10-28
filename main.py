#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import design.file_types_dialog as design
#from tree import Node
from PyQt4 import QtGui, QtCore, uic

class CheckableFileTypes(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(CheckableFileTypes, self).__init__(parent)
        self.checks = {}
        self.root = self.invisibleRootItem()

    def appendRow(self, args):
        return QtGui.QStandardItemModel.appendRow(self, args)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)

        return QtGui.QStandardItemModel.data(self, index, role)

    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return QtCore.Qt.Unchecked

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled

    def setData(self, index, value, role):

        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            #for i, v in self.checks.items():
            #    if are_parent_and_child(index, i):
            #        self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True

        return QtGui.QDirModel.setData(self, index, value, role)

    def exportChecked(self):
        indexes = []
        for index in self.checks.keys():
            if self.checks[index] == QtCore.Qt.Checked:
                indexes.append(index)

        return indexes

def are_parent_and_child(parent, child):
    while child.isValid():
        if child == parent:
            return True
        child = child.parent()
    return False

class CheckableDirModel(QtGui.QDirModel):
    def __init__(self, parent=None):
        QtGui.QDirModel.__init__(self, None)
        self.checks = {}

    def data(self, index, role=QtCore.Qt.DisplayRole):
        #print("data")
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return QtGui.QDirModel.data(self, index, role)

    def flags(self, index):
        return QtGui.QDirModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable

    def checkState(self, index):

        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        print("setdata")
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            for i, v in self.checks.items():
                if are_parent_and_child(index, i):
                    self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True

        return QtGui.QDirModel.setData(self, index, value, role)

    def exportChecked(self, acceptedSuffix=['jpg', 'png', 'bmp']):
        selection = []
        for index in self.checks.keys():
            if self.checks[index] == QtCore.Qt.Checked:
                if os.path.isfile(unicode(self.filePath(index))):
                    #if QtCore.QFileInfo(unicode(self.filePath(index)).split(os.sep)[-1]).completeSuffix().toLower() in acceptedSuffix:
                    selection.append(unicode(self.filePath(index)))
                else:
                    for path, dirs, files in os.walk(unicode(self.filePath(index))):
                        for filename in files:
                            if QtCore.QFileInfo(filename).completeSuffix().toLower() in acceptedSuffix:
                                if self.checkState(self.index(os.path.join(path, filename))) == QtCore.Qt.Checked:
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
        self.scanButton.clicked.connect(self.scan)

        self.fileTypesButton.clicked.connect(self.select_file_types)

    def scan(self):
        self.model.exportChecked()

    def select_file_types(self):
        dialog = FileTypes(self)
        dialog.show()


    def select_folder(self, folder=None):
        if not folder:
            folder = unicode(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
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
        self.model = CheckableFileTypes()
        self.model.setHorizontalHeaderItem(0, QtGui.QStandardItem(""))
        for cat, types in self.categories.items():
            catItem = QtGui.QStandardItem(cat)
            catItem.setCheckable(True)
            for type in types:
                typeItem = QtGui.QStandardItem(type)
                typeItem.setCheckable(True)
                catItem.appendRow(typeItem)
            self.model.appendRow(catItem)
        self.treeView.setModel(self.model)
        self.model.itemChanged.connect(self.item_changet)
        #QtGui.QDialogButtonBox
        QtCore.QObject.connect(self.okCancelBox,QtCore.SIGNAL("accepted()"), self.submit_file_types)
        QtCore.QObject.connect(self.okCancelBox,QtCore.SIGNAL("rejected()"), self.submit_file_types)
        #self.okCanselBox.accepted(self.submit_file_types())

    def item_changet(self, item):
        print(item)

    def submit_file_types(self):
        print(self.model.exportChecked())

    def select_category(self, index):
        print(self.model_category.itemFromIndex(index))
        print(self.model_category.itemFromIndex(index.child(0, 0)))
        print(self.model_category.itemFromIndex(index.child(10, 0)))
        i = 0
        child = self.model_category.itemFromIndex(index.child(i, 0))
        while child:
            self.model_types.appendRow(child)
            i += 1
            child = self.model_category.itemFromIndex(index.child(i, 0))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
