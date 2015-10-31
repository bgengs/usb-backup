import sys, os
from PyQt4 import uic
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt
from checkable_dir import CheckableDirModel
from file_types_window import FileTypes
import thread

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
        self.progressBarScan.setValue(0)

        self.files = []
        self.selected_file_types = {}
        self.progress = 0
        self.scanButton.clicked.connect(self.scan)
        self.fileTypesButton.clicked.connect(self.select_file_types)
        self.backupButtonComp.clicked.connect(self.backup)

    def scan(self):
        #print(self.selected_file_types)
        for element in self.selected_file_types:
            selected = []
            for type, state in element["Types"].items():
                if state == Qt.Checked:
                    selected.append(type)
            if selected:
                for index, state in self.model.checks.items():
                    print("start tread for %s" % element.keys()[0])
                    thread.start_new_thread(self.model.exportChecked, ({index: state}, selected, self.files))

    def backup(self):
        for file in self.files:
            print(file)


    def select_file_types(self):
        dialog = FileTypes(self)
        dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
