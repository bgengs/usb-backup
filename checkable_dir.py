from PyQt4.QtGui import QDirModel
from PyQt4.QtCore import Qt, QFileInfo

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