#!/usr/bin/env python

import sys
if sys.version_info.major < 3: # Python 2
    # Force API version to v2
    import sip
    API_NAMES = ['QDate', 'QDateTime', 'QString', 'QTextStream', 'QTime', 'QUrl', 'QVariant']
    API_VERSION = 2
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)

from PyQt4 import QtGui
from steam_idle_qt.ui.mainwindow import MainWindow
import logging
LOGFMT = '%(asctime)s (%(name)s.%(funcName)s) [%(levelname)s] %(message)s'
if hasattr(sys, 'frozen'):
    import os
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.executable), 'cacert.pem')
logging.basicConfig(format=LOGFMT,
    level=logging.DEBUG,
)
logging.getLogger('requests').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    logger.debug('Creating MainWindow')
    ui = MainWindow()
    logger.debug('Showing MainWindow')
    ui.show()
    logger.debug('About to launch app.exec_()')
    sys.exit(app.exec_())
