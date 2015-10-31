import sys, os
from PyQt4 import uic
from PyQt4.QtGui import QApplication
from checkable_dir import CheckableDirModel
from file_types_window import FileTypes

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
