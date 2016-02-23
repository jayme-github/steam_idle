# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QDialog, QImage, QPixmap, QDialogButtonBox

from .Ui_captcha import Ui_Dialog

class CaptchaDialog(QDialog, Ui_Dialog):
    def __init__(self, image_data, parent=None):
        super(CaptchaDialog, self).__init__(parent)
        self.setupUi(self)
        captchaImage = QImage.fromData(image_data, 'PNG')
        self.labelCaptchaImage.setPixmap(QPixmap.fromImage(captchaImage))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    @pyqtSlot('QString')
    def on_lineEditCaptchaText_textEdited(self, text):
        if len(text) == 6:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

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
