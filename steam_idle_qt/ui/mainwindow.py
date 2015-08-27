# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt4.QtCore import pyqtSlot, Qt, QThread, pyqtSignal
from PyQt4.QtGui import QMainWindow, QTableWidgetItem, QProgressDialog, QPixmap, QIcon

from .Ui_mainwindow import Ui_MainWindow
from steam_idle.page_parser import parse_apps_to_idle

class ParseApps(QThread):
    dataReady = pyqtSignal(dict)
    def run(self):
        apps = parse_apps_to_idle()
        self.dataReady.emit(apps)
        print("thread is done")


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        # TODO: Enable actionStartStop etc.

        # Create a thread for parsing apps and connect signal
        self._threadParseApps = ParseApps()
        self._threadParseApps.dataReady.connect(self.fillTable)

        # Update the tableWidgetGames (e.g. start _threadParseApps)
        self.updateTable()

    def updateTable(self):
        # TODO: _threadParseApps is slow and should be done with progress indication
        self.pr = QProgressDialog(self.tr('Loading data from Steam, please wait'), self.tr('Cancel'), 0, 1, self)
        self.pr.setWindowModality(Qt.WindowModal)
        self.pr.setMinimumDuration(0)
        self.pr.setAutoClose(True)
        self.pr.setValue(0)
        self._threadParseApps.start()


    def fillTable(self, apps):
        def addRow(app):
            """
            Add a game row to the table
            """
            rowId = self.tableWidgetGames.rowCount()
            self.tableWidgetGames.insertRow(rowId)

            # Load pixmap and create an icon
            icon = QIcon(QPixmap(app.icon))

            # Cells are: State, Game, Remaining drops, Playtime
            stateCell = QTableWidgetItem('s')
            gameCell = QTableWidgetItem(icon,str(app.name))
            gameCell.setData(Qt.UserRole, app.appid)
            remainingDropsCell = QTableWidgetItem()
            remainingDropsCell.setData(Qt.EditRole, app.remainingDrops) # Use setData to have numeric instead of alpha-numeric sorting
            playtimeCell = QTableWidgetItem()
            playtimeCell.setData(Qt.EditRole, app.playTime)

            # Add cells
            self.tableWidgetGames.setItem(rowId, 0, stateCell)
            self.tableWidgetGames.setItem(rowId, 1, gameCell)
            self.tableWidgetGames.setItem(rowId, 2, remainingDropsCell)
            self.tableWidgetGames.setItem(rowId, 3, playtimeCell)

        self.tableWidgetGames.clearContents()
        for _, app in apps.items():
            addRow(app)
        self.tableWidgetGames.resizeRowsToContents()
        self.tableWidgetGames.resizeColumnsToContents()
        self.pr.setValue(1)


    @pyqtSlot()
    def on_actionQuit_triggered(self):
        """
        Slot documentation goes here.
        """
        self.close()

    @pyqtSlot()
    def on_actionStartStop_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

    @pyqtSlot()
    def on_actionRefresh_triggered(self):
        self.updateTable()
