#!/usr/bin/env python

from PyQt4 import QtGui
from steam_idle_qt.ui.mainwindow import MainWindow
import logging
logging.basicConfig(format='%(asctime)s (%(name)s.%(funcName)s) [%(levelname)s] %(message)s', level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
#for handler in logging.root.handlers:
#    handler.addFilter(logging.Filter('steamweb'))
#    handler.addFilter(logging.Filter('steam_idle'))
#    handler.addFilter(logging.Filter('steam_idle_qt'))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    logger.debug('Creating MainWindow')
    ui = MainWindow()
    logger.debug('Showing MainWindow')
    ui.show()
    logger.debug('About to launch app.exec_()')
    sys.exit(app.exec_())
