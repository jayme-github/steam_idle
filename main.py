#!/usr/bin/env python

from PyQt4 import QtGui
from steam_idle_qt.ui.mainwindow import MainWindow

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
