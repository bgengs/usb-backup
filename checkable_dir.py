from PyQt4.QtGui import QDirModel, QLabel
from PyQt4.QtCore import Qt, QFileInfo, QModelIndex
import os

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
        self.childs = 0
        self.checked = 0

    def data(self, index, role=Qt.DisplayRole):
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
        if role == Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            for i, v in self.checks.items():
                if are_parent_and_child(index, i):
                    self.checks.pop(i)
            self.checks[index] = value
            #self.childCount(index)
            self.layoutChanged.emit()
            return True

        return QDirModel.setData(self, index, value, role)

    def childCount(self, index):
        self.childs += 1
        i = 0
        child = index.child(i, 0)
        if self.filePath(child):
            print(self.filePath(child))
            self.childCount(child)
        while self.filePath(child):
            i += 1
            child = index.child(i, 0)
            if self.filePath(child):
                print(self.filePath(child))
                self.childCount(child)

    def checkedCount(self, index=QModelIndex()):
        if self.checkState(index) == Qt.Checked:
            self.checked += 1
        i = 0
        child = self.index(i, 0, index)
        if self.filePath(child):
            self.checkedCount(child)
        while self.filePath(child):
            i += 1
            child = self.index(i, 0, index)
            if self.filePath(child):
                self.checkedCount(child)
        return self.checked

    def exportChecked(self, lock, dirs={}, category='', acceptedSuffix=['jpg', 'png', 'bmp'], found={}):
        if not dirs:
            dirs = self.checks
        for index in dirs.keys():
            if dirs[index] == Qt.Checked:
                if os.path.isfile(unicode(self.filePath(index))):
                    found[category].append(os.path.normpath(unicode(self.filePath(index))))
                else:
                    for path, dirs, files in os.walk(unicode(self.filePath(index))):
                        for filename in files:
                            if QFileInfo(filename).completeSuffix().toLower() in acceptedSuffix:
                                if self.checkState(self.index(os.path.join(path, filename))) == Qt.Checked:
                                    found[category].append(os.path.normpath(os.path.join(path, filename)))

        print("ended")
