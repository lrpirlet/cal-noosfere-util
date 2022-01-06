from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import sys

##class Color(QWidget):
##
##    def __init__(self, color):
##        super(Color, self).__init__()
##        self.setAutoFillBackground(True)
##
##        palette = self.palette()
##        palette.setColor(QPalette.Window, QColor(color))
##        self.setPalette(palette)
        
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")

        info_lt = QWidjet.QHBoxLayout

        isbn_tb = QToolBar("ISBN")
        isbn_tb.setIconSize(QSize(20,20))
        self.addToolBar(isbn_tb)

        authors_tb = QToolBar("Auteurs")
        authors_tb.setIconSize(QSize(20,20))
        self.addToolBar(authors_tb)

        title_tb = QToolBar("Titre")
        title_tb.setIconSize(QSize(20,20))
        self.addToolBar(title_tb)

##        layout = QGridLayout()
##
##        layout.addWidget(Color('red'), 0, 0)
##        layout.addWidget(Color('green'), 1, 0)
##        layout.addWidget(Color('blue'), 2, 0)
##        layout.addWidget(Color('purple'), 0, 1)
##        layout.addWidget(Color('yellow'), 1, 1)
##        layout.addWidget(Color('brown'), 2, 1)
##
##        widget = QWidget()
##        widget.setLayout(layout)
##        self.setCentralWidget(widget)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

