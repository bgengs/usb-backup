from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFileSystemModel

def are_parent_and_child(parent, child):
    while child.isValid():
        if child == parent:
            return True
        child = child.parent()
    return False

class Model(QFileSystemModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.checks = {}

    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return Qt.Unchecked

    def data(self, index, role=None):
        if role == Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return QFileSystemModel.data(self, index, role)

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
        return QFileSystemModel.setData(self, index, value, role)

    def flags(self, QModelIndex):

        return Qt.ItemIsUserCheckable | QFileSystemModel.flags(self, QModelIndex)

