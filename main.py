import sys, os, json
from PyQt4 import uic
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QApplication, QInputDialog
from PyQt4.QtCore import Qt, QObject, SIGNAL
from checkable_dir import CheckableDirModel

base, form = uic.loadUiType("design"+os.sep+"secure_usb_backup.ui")
class MainWindow(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.resize(600, 500)
        self.model = CheckableDirModel()
        self.treeViewComputer.setModel(self.model)
        self.treeViewComputer.setIndentation(10)
        self.treeViewComputer.setSortingEnabled(True)
        self.treeViewComputer.setColumnWidth(0, 200)
        self.treeViewComputer.setColumnWidth(1, 80)
        self.treeViewComputer.setColumnWidth(2, 80)
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

base2, form2 = uic.loadUiType("design"+os.sep+"file_types_dialog.ui")
class FileTypes(base2, form2):
    def __init__(self, parent=None):
        super(base2, self).__init__(parent)
        self.setupUi(self)

        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.setHorizontalHeaderItem(0, QStandardItem(""))
        self.model_init(parent)

        QObject.connect(self.okCancelBox, SIGNAL("accepted()"), lambda parent_window=parent: self.submit_file_types(parent_window))
        QObject.connect(self.okCancelBox, SIGNAL("rejected()"), self.close)
        self.newCategButton.clicked.connect(self.add_category)
        self.newTypeButton.clicked.connect(self.add_type)

    def model_init(self, parent_window):
        categories = parent_window.selected_file_types
        if not categories:
            with open('categories.json') as f:
                categories = json.load(f)

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

    def submit_file_types(self, parent_window):
        categories = []
        root = self.model.invisibleRootItem()

        for num_cat in range(root.rowCount()):
            category = root.child(num_cat, 0)
            categories.append({str(category.text()): category.checkState(), "Types": {}})
            for num_type in range(category.rowCount()):
                type = category.child(num_type, 0)
                categories[-1]["Types"].update({str(type.text()): type.checkState()})

        parent_window.selected_file_types = categories
        self.close()

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
            selection = self.treeView.selectedIndexes()[0]
            self.model.itemFromIndex(selection).appendRow(catType)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
