from PyQt4.QtGui import QStandardItemModel, QStandardItem, QInputDialog, QMenu, QDialog
from PyQt4.QtCore import Qt, QObject, SIGNAL
from PyQt4 import uic
from os import sep
from json import load, dump

base2, form2 = uic.loadUiType("design"+sep+"file_types_dialog.ui")
class FileTypes(base2, form2):
    def __init__(self, parent=None):
        super(base2, self).__init__(parent)
        self.setupUi(self)

        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.setHorizontalHeaderItem(0, QStandardItem(""))
        self.model_init()

        self.saveButton.clicked.connect(self.save)
        self.okCancelBox.accepted.connect(self.accept)
        self.okCancelBox.rejected.connect(self.reject)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)
        self.treeView.setToolTip('Here you can select file types that you want to find. Also you can\nadd new category or file type. Click right button on it.')

    def model_init(self):
        categories = {}
        if not categories:
            with open('categories.json') as f:
                categories = load(f)

        for element in categories:
            catItem = QStandardItem(element.keys()[0])
            catItem.setCheckable(True)
            catItem.setCheckState(element[element.keys()[0]])
            for type_name, check_state in element["Types"].items():
                typeItem = QStandardItem(type_name)
                typeItem.setCheckable(True)
                typeItem.setCheckState(check_state)
                catItem.appendRow(typeItem)
            self.model.appendRow(catItem)
        self.treeView.setModel(self.model)
        self.submit_file_types()

    def quit(self):
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

    def submit_file_types(self):
        categories = []
        root = self.model.invisibleRootItem()

        for num_cat in range(root.rowCount()):
            category = root.child(num_cat, 0)
            categories.append({str(category.text()): category.checkState(), "Types": {}})
            for num_type in range(category.rowCount()):
                type = category.child(num_type, 0)
                categories[-1]["Types"].update({str(type.text()): type.checkState()})
        return categories

    def openMenu(self, position):
        level = 0
        index = self.treeView.selectedIndexes()[0]
        while index.parent().isValid():
            index = index.parent()
            level += 1

        menu = QMenu()
        if level == 0:
            menu.addAction(self.tr("Add category"), self.add_category)
            menu.addAction(self.tr("Add type"), self.add_type)
            menu.addAction(self.tr("Remove"), self.remove)
        elif level == 1:
            menu.addAction(self.tr("Add type"), self.add_type)
            menu.addAction(self.tr("Remove"), self.remove)

        menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def add_category(self):
        text, ok = QInputDialog.getText(self, 'Create new category', 'Category name:')
        if ok:
            catItem = QStandardItem(text)
            catItem.setCheckable(True)
            self.model.appendRow(catItem)
            #self.label.setText(unicode(text))

    def add_type(self):
        text, ok = QInputDialog.getText(self, 'Add new type', 'Postfix:')
        if ok:
            catType = QStandardItem(text)
            catType.setCheckable(True)
            index = self.treeView.selectedIndexes()[0]
            if self.model.itemFromIndex(index).hasChildren():
                self.model.itemFromIndex(index).appendRow(catType)
            else:
                self.model.itemFromIndex(index).parent().appendRow(catType)

    def save(self):
        with open('categories.json', 'w') as f:
            dump(self.submit_file_types(), f)

    def remove(self):
        index = self.treeView.selectedIndexes()[0]
        parent = self.model.itemFromIndex(index).parent()
        if parent:
            self.model.removeRow(index.row(), parent.index())
        else:
            parent = self.model.invisibleRootItem()
            self.model.removeRow(index.row(), parent.index())

    @staticmethod
    def call():
        dialog = FileTypes()
        result = dialog.exec_()
        categories = dialog.submit_file_types()
        return categories, result == QDialog.Accepted