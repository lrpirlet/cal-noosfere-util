#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPL v3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>
####
####
####from PyQt5.Qt import QUrl
####from PyQt5.QtWebEngineWidgets import QWebEngineView
####
from calibre.gui2 import Application
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

import tempfile
import os
import sys

class MainWindow(QMainWindow):

#    def __init__(self, *args, **kwargs):
    def __init__(self, data):
        #super(MainWindow,self).__init__(*args, **kwargs)
        super().__init__()

        # data = [url, isbn, auteurs, titre]
        self.isbn, self.auteurs, self.titre = data[1], data[2], data[3]

        self.browser = QWebEngineView()
        self.browser.resize(1200,900)
        self.browser.setUrl(QUrl("http://www.google.com"))

        self.setCentralWidget(self.browser)

  # set info toolbar
        info_tb = QToolBar("Get")
        info_tb.setIconSize(QSize(60,30))
        self.addToolBar(Qt.BottomToolBarArea, info_tb)

        ISBN_btn = QAction(get_icons('blue_icon/ISBN.png'), "ISBN", self)
        ISBN_btn.setStatusTip("Montre et copie le ISBN dans le presse-papier pour coller dans Mots-clefs à rechercher")
                                # Show authors, copy in clipboard to paste in search field of noosfere
        ISBN_btn.triggered.connect(self.set_isbn_info)
        info_tb.addAction(ISBN_btn)

        Auteurs_btn = QAction(get_icons('blue_icon/Auteurs.png'), "Auteur(s)", self)
        Auteurs_btn.setStatusTip("Montre et copie le(s) Auteur(s) dans le presse-papier pour coller dans Mots-clefs à rechercher")
                                # Show authors, copy in clipboard to paste in search field of noosfere
        Auteurs_btn.triggered.connect(self.set_auteurs_info)
        info_tb.addAction(Auteurs_btn)

        Titre_btn = QAction(get_icons('blue_icon/Titre.png'), "Titre", self)
        Titre_btn.setStatusTip("Montre le Titre")                                   # show title
        Titre_btn.triggered.connect(self.set_titre_info)
        info_tb.addAction(Titre_btn)

        self.infobox = QLineEdit()
        self.infobox.setReadOnly(True)
        self.infobox.setStatusTip(" Aucune action, ce box montre l'ISBN, le(s) Auteur(s) ou le Titre, protégé en écriture."
                                  " Tout ou partie du texte peut être sélectionné pour copier et coller")
                                 # No action, this box displays the ISBN, the Author(s) or the Title, in write protect.
                                 # Part or the whole text may be selected for copy paste.
        info_tb.addWidget(self.infobox)

  # set navigation toolbar
        nav_tb = QToolBar("Navigation")
        nav_tb.setIconSize(QSize(20,20))
        self.addToolBar(nav_tb)

        home_btn = QAction(get_icons('blue_icon/home.png'), "Home", self)
        home_btn.setStatusTip("On va à la une de noosfere")                         # We go to the front page of noosfere
        home_btn.triggered.connect(self.navigate_home)
        nav_tb.addAction(home_btn)

        back_btn = QAction(get_icons('blue_icon/back.png'), "Back", self)
        back_btn.setStatusTip("On revient à la page précédente")                    # Back to the previous page
        back_btn.triggered.connect(self.browser.back)
        nav_tb.addAction(back_btn)

        next_btn = QAction(get_icons('blue_icon/forward.png'), "Forward", self)
        next_btn.setStatusTip("On retourne à la page suivante")                     # Back to the next page
        next_btn.triggered.connect(self.browser.forward)
        nav_tb.addAction(next_btn)

        reload_btn = QAction(get_icons('blue_icon/reload.png'), "Reload", self)
        reload_btn.setStatusTip("On recharge la page")                              # Reload the page
        reload_btn.triggered.connect(self.browser.reload)
        nav_tb.addAction(reload_btn)

        stop_btn = QAction(get_icons('blue_icon/stop.png'), "Stop", self)
        stop_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        stop_btn.triggered.connect(self.browser.stop)
        nav_tb.addAction(stop_btn)

        self.urlbox = QLineEdit()
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.urlbox.setStatusTip("Tu peut même introduire une adresse, hors noosfere, mais A TES RISQUES ET PERILS... noosfere est sûr ( https:// ), la toile par contre...")
                                # You can even enter an address, outside of noosfere, but AT YOUR OWN RISK... noosfere is safe: ( https:// ), the web on the other side...
        nav_tb.addWidget(self.urlbox)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadStarted.connect(self.loading_title)
        self.browser.loadFinished.connect(self.update_title)

        abort_btn = QAction(get_icons('blue_icon/abort.png'), "Abort", self)
        abort_btn.setStatusTip("On arrête tout, on oublie tout et on ne change rien")
                              # Stop everything, forget everything and change nothing
        abort_btn.triggered.connect(self.close)
        nav_tb.addAction(abort_btn)

        exit_btn = QAction(get_icons('blue_icon/exit.png'), "Select and exit", self)
        exit_btn.setStatusTip("On sélectionne cet URL pour extraction de nsfr_id, on continue")
                             # select this URL for extraction of nsfr_id, continue
        exit_btn.triggered.connect(self.select_and_exit)
        nav_tb.addAction(exit_btn)

        self.show()
        self.setStatusBar(QStatusBar(self))

  # get info actions
    @pyqtSlot()
    def set_isbn_info(self):
        self.infobox.setText( self.isbn )
        cb = Application.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.isbn.replace("-",""), mode=cb.Clipboard)

    @pyqtSlot()
    def set_auteurs_info(self):
        self.infobox.setText( self.auteurs )
        cb = Application.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.auteurs, mode=cb.Clipboard)

    @pyqtSlot()
    def set_titre_info(self):
        self.infobox.setText( self.titre )

  # Navigation actions
    def initial_url(self,url="http://www.google.com"):
        self.browser.setUrl(QUrl(url))
        cb = Application.clipboard()
        #self.urlbox.setText(url)

    def navigate_home(self):
        self.browser.setUrl( QUrl("https://www.noosfere.org/") )

    def navigate_to_url(self):                    # Does not receive the Url
        q = QUrl( self.urlbox.text() )
        self.browser.setUrl(q)

    def update_urlbar(self, q):
        self.urlbox.setText( q.toString() )
        self.urlbox.setCursorPosition(0)

    def loading_title(self):
        title="En téléchargement de l'url"
        self.setWindowTitle(title)

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def select_and_exit(self):                    #sent q over the clipboard then exit
        cb = Application.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.urlbox.text(), mode=cb.Clipboard)
        qApp.quit()     # exit application

    def closeEvent(self, event):                  # hit window exit "X" button
        qDebug('MainWindow.closeEvent()')
        reply = QMessageBox.question(self, 'Vraiment', "Quitter et ne rien changer", QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            super().closeEvent(event)
        else:
            event.ignore()


def main(data):
    #     def launch_gui_app(self, name, args=(), kwargs=None, description=''):
    #         job = ParallelJob(name, description, lambda x: x,
    #                 args=list(args), kwargs=kwargs or {})
    #         self.serverserver.run_job(job, gui=True, redirect_output=False)
    #
    # from jobs.py in gui2 in calibre in src...
    #
    # self.gui.job_manager.launch_gui_app('webengine-dialog', kwargs={'module':'calibre_plugins.noosfere_util.main', 'url':url})

    # Initialize environment..

    # create a temp file... while it exists ui.py will wait... this file will disappear with the process
    tfp=tempfile.NamedTemporaryFile(prefix="sync-cal-qweb")
    # tfp=tempfile.NamedTemporaryFile(prefix="sync-cal-qweb",mode='w+',buffering=1, delete=False)
    # tfp.write(str(type(data))+"\n")
    # tfp.write("data : "+str(data)+"\n")

    # retrieve component from data
    #        data = [url, isbn, auteurs, titre]
    url, isbn, auteurs, titre = data[0], data[1], data[2], data[3]

    # tfp.write("url     : "+url+"\n")
    # tfp.write("isbn    : "+isbn+"\n")
    # tfp.write("auteurs : "+auteurs+"\n")
    # tfp.write("titre   : "+titre+"\n")

    # Start QWebEngineView and associated widgets
    app = Application([])
    window = MainWindow(data)
    window.initial_url(url)
    app.exec_()

    # signal ui.py that we are finished
    tfp.close           # close temp file
