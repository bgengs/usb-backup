#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import design.secure_usb_backup as design
from PyQt4 import QtGui, QtCore

class Node(object):
    def __init__(self, name, path, parent=None):
        self._name = name
        self._path = path
        self._children = []
        self._parent = parent
        if parent is not None:
            parent.add_child(self)

    def add_child(self, child):
        self._children.append(child)

    def name(self):
        return self._name

    def path(self):
        return self._path

    def child_count(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def child(self, row):
        return self._children[row]

    def row(self):
        if self.parent() is not Node:
            return self.parent()._children.index(self)

class FilesModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(FilesModel, self).__init__(parent)
        self._root = root

    def rowCount(self, parent):
        if not parent.isValid():
            return self._root.child_count()
        else:
            return parent.internalPointer().child_count()

    def columnCount(self, parent):
        return 2

    def data(self, index, role=None):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return node.name()
            else:
                return node.path()


    def setData(self, QModelIndex, QVariant, int_role=None):
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "File name"
            else:
                return  "System path"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._root

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()

        return success

if __name__ == '__main__':
    root = Node("root", "")
    disc_c = Node("C", "", root)
    temp = Node("temp", "", disc_c)
    file = Node("photo.jpg", "C:/temp/photo.jpg", temp)
    disc_d = Node("D", "", root)
    users = Node("users", "", disc_d)
    spam = Node("spam", "", users)
    egg = Node("chicken.egg", "D:/users/spam/chicken.egg", spam)
    model_computer = FilesModel(root)

    root_storage = Node("", "")
    alexey = Node("Alexey PC", "", root_storage)
    documents = Node("Documents", "", alexey)
    req = Node("requirements.docx", "C:/users/Alexey/Desktop/requirements.docx", documents)
    book = Node("orange book.pdf", "C:/Program Files/orange book.pdf", documents)
    images = Node("Images", "", alexey)
    photo = Node("myphoto.jpg", "D:/photos/myphoto.jpg", images)
    develop = Node("Develop", "", alexey)

    bernie = Node("Bernie Mac", "", root_storage)
    documents_b = Node("Documents", "", bernie)
    model_storage = FilesModel(root_storage)


    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    ui = design.Ui_main_window()
    ui.setupUi(window)
    ui.treeViewComputer.setModel(model_computer)
    ui.treeViewStorage.setModel(model_storage)
    window.show()
    sys.exit(app.exec_())
