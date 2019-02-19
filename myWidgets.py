
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ClickableLabel(QLabel):

    clicked = pyqtSignal()

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button () == 1:  # will only emit on left click
            self.clicked.emit()


