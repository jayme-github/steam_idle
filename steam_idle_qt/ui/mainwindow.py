# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow, QTableWidgetItem

from .Ui_mainwindow import Ui_MainWindow
from steam_idle.page_parser import parse_badges_page


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
        # TODO: Get games from steam_idle
        # TODO: Fill games in ListView (oder by whatever)
        # TODO: Enable actionStartStop etc.
        for app in parse_badges_page():
            print(app)
            self.addRow(*app)


    def addRow(self, game, remainingDrops, playtime):
        """
        Add a game row to the table
        """
        rowId = self.tableWidgetGames.rowCount()
        self.tableWidgetGames.insertRow(rowId)

        # Cells are: State, Game, Remaining drops, Playtime
        stateCell = QTableWidgetItem("FOo")
        gameCell = QTableWidgetItem(str(game)) #TODO: Add game icone
        remainingDropsCell = QTableWidgetItem(str(remainingDrops))
        playtimeCell = QTableWidgetItem(str(playtime))

        # Add cells
        self.tableWidgetGames.setItem(rowId, 0, stateCell)
        self.tableWidgetGames.setItem(rowId, 1, gameCell)
        self.tableWidgetGames.setItem(rowId, 2, remainingDropsCell)
        self.tableWidgetGames.setItem(rowId, 3, playtimeCell)

        self.tableWidgetGames.resizeRowToContents(rowId)
        self.tableWidgetGames.resizeColumnsToContents()

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
