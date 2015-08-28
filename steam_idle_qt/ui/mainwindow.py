# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt4.QtCore import pyqtSlot, Qt, QThread, pyqtSignal
from PyQt4.QtGui import QMainWindow, QTableWidgetItem, QProgressBar, QPixmap, QIcon

from .Ui_mainwindow import Ui_MainWindow
from steam_idle.page_parser import parse_apps_to_idle

class ParseApps(QThread):
    dataReady = pyqtSignal(dict)
    def run(self):
        apps = parse_apps_to_idle()
        self.dataReady.emit(apps)


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
        self.statusBar.setMaximumHeight(20)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,1)
        self.progressBar.setFormat('')
        self.progressBar.setMaximumHeight(self.statusBar.height())
        self.statusBar.addPermanentWidget(self.progressBar)

        # TODO: Enable actionStartStop etc.

        # Create a thread for parsing apps and connect signal
        self._threadParseApps = ParseApps()
        self._threadParseApps.dataReady.connect(self.fillTable)

        # Update the tableWidgetGames (e.g. start _threadParseApps)
        self.updateTable()

    def startProgressBar(self, message, timeout=0):
        self.statusBar.showMessage(message)
        self.progressBar.setRange(0,0)

    def stopProgressBar(self):
        self.statusBar.clearMessage()
        self.progressBar.setRange(0,1)

    def updateTable(self):
        self.startProgressBar('Loading data from Steam...')
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
        self.tableWidgetGames.setRowCount(0)
        for _, app in apps.items():
            addRow(app)
        self.tableWidgetGames.resizeColumnsToContents()
        self.tableWidgetGames.resizeRowsToContents()
        self.stopProgressBar()


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
