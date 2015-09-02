#!/usr/bin/env python

from PyQt4 import QtGui
from steam_idle_qt.ui.mainwindow import MainWindow
import logging
logging.basicConfig(format='%(asctime)s (%(name)s.%(funcName)s) [%(levelname)s] %(message)s', level=logging.DEBUG)
for handler in logging.root.handlers:
    handler.addFilter(logging.Filter('steamweb'))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
