#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPL v3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>
####
####
####from PyQt5.Qt import QUrl
####from PyQt5.QtWebEngineWidgets import QWebEngineView
####
####from calibre.gui2 import Application
####
####
####def main(url):
####    # This function is run in a separate process and can do anything it likes,
####    # including use QWebEngine. Here it simply opens the passed in URL
####    # in a QWebEngineView
####    app = Application([])
####    w = QWebEngineView()
####    w.setUrl(QUrl(url))
####    w.setGeometry(300, 300, 1000, 700)
####    w.setWindowTitle('Selectionne le volume voulu')
####    w.show()
####    w.raise_()
####    app.exec_()
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import sys
#import os

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setGeometry(300, 300, 1200, 800)
        self.browser.setUrl(QUrl("http://www.google.com"))

        self.setCentralWidget(self.browser)

        navtb = QToolBar("Navigation")
        navtb.setIconSize( QSize(80,25) )
        self.addToolBar(navtb)

        back_btn = QAction( QIcon('pitr_green_double_arrows_set_1.png'), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect( self.browser.back )
        navtb.addAction(back_btn)

        next_btn = QAction( QIcon('pitr_green_double_arrows_set_2.png'), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect( self.browser.forward )
        navtb.addAction(next_btn)

        reload_btn = QAction( QIcon('refresh-icon4533.png'), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect( self.browser.reload )
        navtb.addAction(reload_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect( self.navigate_to_url )
        navtb.addWidget(self.urlbar)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)

        exit_btn = QAction( QIcon('exit150-33.png'), "Select and exit", self)
        exit_btn.setStatusTip("Select URL and exit to calibre")
        exit_btn.triggered.connect( self.select_and_exit )
        navtb.addAction(exit_btn)

        self.show()

    def initial_url(self,url="http://www.google.com"):
        self.browser.setUrl(QUrl(url))

    def navigate_to_url(self): # Does not receive the Url
        q = QUrl( self.urlbar.text() )
        self.browser.setUrl(q)

    def update_urlbar(self, q):
        self.urlbar.setText( q.toString() )
        self.urlbar.setCursorPosition(0)

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def select_and_exit(self):
        # sent q to the queue wait till consumed then exit
        print("nous sommes à l'URL", self.urlbar.text(),"\nNow exiting")
        sys.exit("done")
        # need to push the address to calling process using the queue opened
        
def main(url):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.initial_url(url)
    app.exec_()
