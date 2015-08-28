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
    actionStartStopShowsStart = True # Does the Start/Stop button show the start icon?

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        self.labelTotalGamesToIdle.hide()
        self.labelTotalGamesInRefund.hide()
        self.labelTotalRemainingDrops.hide()
        self.statusBar.setMaximumHeight(20)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,1)
        self.progressBar.setFormat('')
        self.progressBar.setMaximumHeight(self.statusBar.height())
        self.statusBar.addPermanentWidget(self.progressBar)

        self.tableWidgetGames.selectionModel().currentRowChanged.connect(self.on_tableWidgetGamesSelectionModel_currentRowChanged)
        # TODO: Enable actionStartStop etc.

        # Create a thread for parsing apps and connect signal
        self._threadParseApps = ParseApps()
        self._threadParseApps.dataReady.connect(self.updateDataFromSteam)

        # Update the tableWidgetGames (e.g. start _threadParseApps)
        self.on_actionRefresh_triggered()

    def startProgressBar(self, message, timeout=0):
        self.statusBar.showMessage(message)
        self.progressBar.setRange(0,0)

    def stopProgressBar(self):
        self.statusBar.clearMessage()
        self.progressBar.setRange(0,1)

    def updateDataFromSteam(self, apps):
        ''' Update UI with data from steam
        '''
        def addRow(app):
            # Add a game row to the table
            rowId = self.tableWidgetGames.rowCount()
            self.tableWidgetGames.insertRow(rowId)

            # Load pixmap and create an icon
            icon = QIcon(QPixmap(app.icon))

            # Cells are: State, Game, Remaining drops, Playtime
            stateCell = QTableWidgetItem('s')
            gameCell = QTableWidgetItem(icon,str(app.name))
            gameCell.setData(Qt.UserRole, app)
            remainingDropsCell = QTableWidgetItem()
            remainingDropsCell.setData(Qt.EditRole, app.remainingDrops) # Use setData to have numeric instead of alpha-numeric sorting
            playtimeCell = QTableWidgetItem()
            playtimeCell.setData(Qt.EditRole, app.playTime)

            # Add cells
            self.tableWidgetGames.setItem(rowId, 0, stateCell)
            self.tableWidgetGames.setItem(rowId, 1, gameCell)
            self.tableWidgetGames.setItem(rowId, 2, remainingDropsCell)
            self.tableWidgetGames.setItem(rowId, 3, playtimeCell)

        # Clear table
        self.tableWidgetGames.clearContents()
        self.tableWidgetGames.setRowCount(0)

        totalRemainingDrops = 0
        gamesInRefundPeriod = 0
        for _, app in apps.items():
            totalRemainingDrops += app.remainingDrops
            if app.playTime < 2.0:
                gamesInRefundPeriod += 1
            addRow(app)
        self.tableWidgetGames.selectRow(0)

        # Update cell and row sizes
        self.tableWidgetGames.resizeColumnsToContents()
        self.tableWidgetGames.resizeRowsToContents()

        # Update labels
        self.labelTotalGamesToIdle.setText(self.tr('{} games left to idle').format(len(apps)))
        self.labelTotalGamesToIdle.show()
        self.labelTotalGamesInRefund.setText(self.tr('{} games in refund period (<2h play time)').format(gamesInRefundPeriod)) # TODO: Highlight games in refund on click
        self.labelTotalGamesInRefund.show()
        self.labelTotalRemainingDrops.setText(self.tr('{} remaining card drops').format(totalRemainingDrops))
        self.labelTotalRemainingDrops.show()

        # Done
        self.stopProgressBar()

        if len(apps) > 0:
            self.actionStartStop.enable()


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
        if self.actionStartStopShowsStart:
            icon = QIcon.fromTheme("media-playback-stop")
        else:
            icon = QIcon.fromTheme("media-playback-start")

        self.actionStartStop.setIcon(icon)

    @pyqtSlot()
    def on_actionRefresh_triggered(self):
        self.startProgressBar('Loading data from Steam...')
        self._threadParseApps.start()

    def on_tableWidgetGamesSelectionModel_currentRowChanged(self, current, previous):
        #print('current:', current.row(), 'previous:', previous.row())
        gameCell = self.tableWidgetGames.item(current.row(), 1) # Get the gameCell of this row
        app = gameCell.data(Qt.UserRole)
        headerPixmap = QPixmap(app.header)
        self.labelHeaderImage.setPixmap(headerPixmap)
