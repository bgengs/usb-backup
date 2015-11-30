from PyQt4.QtCore import Qt, QFileInfo
from PyQt4.QtGui import QFileSystemModel
from os import path, sep, walk

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

    def exportChecked(self, lock, dirs={}, found={}):
        if not dirs:
            dirs = self.checks
        for index in dirs.keys():
            if dirs[index] == Qt.Checked:
                if path.isfile(unicode(self.filePath(index))):
                    file_dir_path = unicode(self.filePath(index)).split(sep)
                    print(file_dir_path)
                    storage = file_dir_path[-4].split('/')[-1]
                    date = file_dir_path[-3]
                    category = file_dir_path[-2]
                    if storage not in found.keys():
                        found.update({storage: {}})
                    if category not in found[storage].keys():
                        found[storage].update({category: {}})
                    if date not in found[storage][category].keys():
                        found[storage][category].update({date: []})
                    found[storage][category][date].append(path.normpath(file_dir_path[-1]))
                else:
                    for cur_path, dirs, files in walk(unicode(self.filePath(index))):
                        for filename in files:
                            if self.checkState(self.index(path.join(cur_path, filename))) == Qt.Checked and filename!='init':
                                file_dir_path = cur_path.split(sep)
                                storage = file_dir_path[-3].split('/')[-1]
                                date = file_dir_path[-2]
                                category = file_dir_path[-1]
                                if storage not in found.keys():
                                    found.update({storage: {}})
                                if category not in found[storage].keys():
                                    found[storage].update({category: {}})
                                if date not in found[storage][category].keys():
                                    found[storage][category].update({date: []})
                                found[storage][category][date].append(filename)
        print('ended')