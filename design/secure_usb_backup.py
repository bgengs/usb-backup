# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\��������� ����\��������\python\secure_backup\design\secure_usb_backup.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName(_fromUtf8("main_window"))
        main_window.setEnabled(True)
        main_window.resize(319, 500)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(sizePolicy)
        main_window.setMinimumSize(QtCore.QSize(300, 500))
        self.centralWidget = QtGui.QWidget(main_window)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayoutMainWindow = QtGui.QGridLayout(self.centralWidget)
        self.gridLayoutMainWindow.setMargin(11)
        self.gridLayoutMainWindow.setSpacing(6)
        self.gridLayoutMainWindow.setObjectName(_fromUtf8("gridLayoutMainWindow"))
        self.tabWidgetRoot = QtGui.QTabWidget(self.centralWidget)
        self.tabWidgetRoot.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidgetRoot.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidgetRoot.setMovable(False)
        self.tabWidgetRoot.setObjectName(_fromUtf8("tabWidgetRoot"))
        self.tab_computer = QtGui.QWidget()
        self.tab_computer.setObjectName(_fromUtf8("tab_computer"))
        self.gridLayoutComputer = QtGui.QGridLayout(self.tab_computer)
        self.gridLayoutComputer.setMargin(11)
        self.gridLayoutComputer.setSpacing(6)
        self.gridLayoutComputer.setObjectName(_fromUtf8("gridLayoutComputer"))
        self.filesFoundLabel = QtGui.QLabel(self.tab_computer)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.filesFoundLabel.setFont(font)
        self.filesFoundLabel.setObjectName(_fromUtf8("filesFoundLabel"))
        self.gridLayoutComputer.addWidget(self.filesFoundLabel, 0, 0, 1, 1)
        self.treeViewComputer = QtGui.QTreeView(self.tab_computer)
        self.treeViewComputer.setObjectName(_fromUtf8("treeViewComputer"))

        self.gridLayoutComputer.addWidget(self.treeViewComputer, 1, 0, 6, 1)
        self.foldersButton = QtGui.QPushButton(self.tab_computer)
        self.foldersButton.setObjectName(_fromUtf8("foldersButton"))
        self.gridLayoutComputer.addWidget(self.foldersButton, 1, 1, 1, 1)
        self.fileTypesButton = QtGui.QPushButton(self.tab_computer)
        self.fileTypesButton.setObjectName(_fromUtf8("fileTypesButton"))
        self.gridLayoutComputer.addWidget(self.fileTypesButton, 2, 1, 1, 1)
        self.scanButton = QtGui.QPushButton(self.tab_computer)
        self.scanButton.setObjectName(_fromUtf8("scanButton"))
        self.gridLayoutComputer.addWidget(self.scanButton, 3, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 242, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayoutComputer.addItem(spacerItem, 4, 1, 1, 1)
        self.backupScanButton = QtGui.QPushButton(self.tab_computer)
        self.backupScanButton.setObjectName(_fromUtf8("backupScanButton"))
        self.gridLayoutComputer.addWidget(self.backupScanButton, 5, 1, 1, 1)
        self.helpButton = QtGui.QPushButton(self.tab_computer)
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.gridLayoutComputer.addWidget(self.helpButton, 6, 1, 1, 1)
        self.progressBarScan = QtGui.QProgressBar(self.tab_computer)
        self.progressBarScan.setProperty("value", 0)
        self.progressBarScan.setObjectName(_fromUtf8("progressBarScan"))
        self.gridLayoutComputer.addWidget(self.progressBarScan, 7, 0, 1, 1)
        self.filesFoundLabel.raise_()
        self.foldersButton.raise_()
        self.fileTypesButton.raise_()
        self.scanButton.raise_()
        self.backupScanButton.raise_()
        self.helpButton.raise_()
        self.progressBarScan.raise_()
        self.treeViewComputer.raise_()
        self.tabWidgetRoot.addTab(self.tab_computer, _fromUtf8(""))
        self.tab_storage = QtGui.QWidget()
        self.tab_storage.setObjectName(_fromUtf8("tab_storage"))
        self.gridLayoutStorage = QtGui.QGridLayout(self.tab_storage)
        self.gridLayoutStorage.setMargin(11)
        self.gridLayoutStorage.setSpacing(6)
        self.gridLayoutStorage.setObjectName(_fromUtf8("gridLayoutStorage"))
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayoutStorage.addItem(spacerItem1, 4, 1, 1, 1)
        self.newStorageButton = QtGui.QPushButton(self.tab_storage)
        self.newStorageButton.setObjectName(_fromUtf8("newStorageButton"))
        self.gridLayoutStorage.addWidget(self.newStorageButton, 3, 1, 1, 1)
        self.storageStructLabel = QtGui.QLabel(self.tab_storage)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.storageStructLabel.setFont(font)
        self.storageStructLabel.setObjectName(_fromUtf8("storageStructLabel"))
        self.gridLayoutStorage.addWidget(self.storageStructLabel, 0, 0, 1, 1)
        self.restoreButton = QtGui.QPushButton(self.tab_storage)
        self.restoreButton.setObjectName(_fromUtf8("restoreButton"))
        self.gridLayoutStorage.addWidget(self.restoreButton, 2, 1, 1, 1)
        self.backupButtonStrorage = QtGui.QPushButton(self.tab_storage)
        self.backupButtonStrorage.setObjectName(_fromUtf8("backupButtonStrorage"))
        self.gridLayoutStorage.addWidget(self.backupButtonStrorage, 1, 1, 1, 1)
        self.progressBarBackup = QtGui.QProgressBar(self.tab_storage)
        self.progressBarBackup.setProperty("value", 87)
        self.progressBarBackup.setObjectName(_fromUtf8("progressBarBackup"))
        self.gridLayoutStorage.addWidget(self.progressBarBackup, 6, 0, 1, 1)
        self.treeViewStorage = QtGui.QTreeView(self.tab_storage)
        self.treeViewStorage.setObjectName(_fromUtf8("treeViewStorage"))
        self.gridLayoutStorage.addWidget(self.treeViewStorage, 1, 0, 5, 1)
        self.helpButtonStorage = QtGui.QPushButton(self.tab_storage)
        self.helpButtonStorage.setObjectName(_fromUtf8("helpButtonStorage"))
        self.gridLayoutStorage.addWidget(self.helpButtonStorage, 5, 1, 1, 1)
        self.tabWidgetRoot.addTab(self.tab_storage, _fromUtf8(""))
        self.gridLayoutMainWindow.addWidget(self.tabWidgetRoot, 0, 0, 1, 1)
        main_window.setCentralWidget(self.centralWidget)

        self.retranslateUi(main_window)
        self.tabWidgetRoot.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        main_window.setWindowTitle(_translate("main_window", "Secure USB backup", None))
        self.filesFoundLabel.setText(_translate("main_window", "Files found", None))
        self.foldersButton.setText(_translate("main_window", "Folders", None))
        self.fileTypesButton.setText(_translate("main_window", "File types", None))
        self.scanButton.setText(_translate("main_window", "Scan", None))
        self.backupScanButton.setText(_translate("main_window", "Backup", None))
        self.helpButton.setText(_translate("main_window", "Help", None))
        self.tabWidgetRoot.setTabText(self.tabWidgetRoot.indexOf(self.tab_computer), _translate("main_window", "Computer", None))
        self.newStorageButton.setText(_translate("main_window", "New storage", None))
        self.storageStructLabel.setText(_translate("main_window", "Storage structure ", None))
        self.restoreButton.setText(_translate("main_window", "Restore", None))
        self.backupButtonStrorage.setText(_translate("main_window", "Backup", None))
        self.helpButtonStorage.setText(_translate("main_window", "Help", None))
        self.tabWidgetRoot.setTabText(self.tabWidgetRoot.indexOf(self.tab_storage), _translate("main_window", "HDD Storage", None))

