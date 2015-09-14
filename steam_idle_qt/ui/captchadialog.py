# -*- coding: utf-8 -*-

"""
Module implementing CaptchaDialog.
"""

#from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QDialog, QImage, QPixmap

from .Ui_captcha import Ui_Dialog

class CaptchaDialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, image_data, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        captchaImage = QImage.fromData(image_data, 'PNG')
        self.labelCaptchaImage.setPixmap(QPixmap.fromImage(captchaImage))

#    @pyqtSlot()
#    def on_buttonBox_accepted(self):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError

if __name__ == "__main__":
    import sys, random
    from PyQt4.QtGui import QApplication
    from png import Writer
    from io import BytesIO
    f = BytesIO()
    w = Writer(206, 40)
    pngdata = [[random.randint(0,255) for i in range(206*w.planes)] for i in range(40)]
    w.write(f, pngdata)
    app = QApplication(sys.argv)
    captchaDialog = CaptchaDialog(image_data=f.getvalue())
    captchaDialog.exec_()
    print('CaptchaText: "%s"' % captchaDialog.lineEditCaptchaText.text())
    sys.exit(app.exec_())
