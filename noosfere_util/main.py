#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPL v3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>

from PyQt5.QtCore import pyqtSlot, qDebug, QUrl, QSize
from PyQt5.QtWidgets import (QMainWindow, QApplication, QToolBar, QAction, QLineEdit,
                                QStatusBar, QMessageBox, qApp, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton, QShortcut)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from calibre.gui2 import Application
import tempfile
import os
import sys

class MainWindow(QMainWindow):

    def __init__(self, data):
        super().__init__()

        # data = [url, isbn, auteurs, titre]
        self.isbn, self.auteurs, self.titre = data[1].replace("-",""), data[2], data[3]

        qDebug("isbn    : "+self.isbn)
        qDebug("auteurs : "+str(self.auteurs.encode('utf-8')))
        qDebug("titre   : "+str(self.titre.encode('utf-8')))

        self.cb = Application.clipboard()

  # browser
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))

  # info boxes isbn
        self.isbn_btn = QPushButton(" ISBN ", self)
        self.isbn_btn.setStatusTip("Copie le ISBN dans le presse-papier pour coller dans Mots-clefs à rechercher")
                                   # Show authors, copy in clipboard to paste in search field of noosfere
        self.isbn_btn.clicked.connect(self.set_isbn_info)

        self.isbn_dsp = QLineEdit()
        self.isbn_dsp.setReadOnly(True)
        self.isbn_dsp.setText(self.isbn)
        self.isbn_dsp.setStatusTip(" Aucune action, cette boite montre l'ISBN protégé en écriture."
                                   " Tout ou partie du texte peut être sélectionné pour copier et coller")
                                   # No action, this box displays the ISBN write protected.
                                   # Part or the whole text may be selected for copy paste.

        self.isbn_lt = QHBoxLayout()
        self.isbn_lt.addWidget(self.isbn_btn)
        self.isbn_lt.addWidget(self.isbn_dsp)

  # info boxes auteurs
        self.auteurs_btn = QPushButton("Auteur(s)", self)
        self.auteurs_btn.setStatusTip("Copie le(s) Auteur(s) dans le presse-papier pour coller dans Mots-clefs à rechercher")
                                      # Show authors, copy in clipboard to paste in search field of noosfere
        self.auteurs_btn.clicked.connect(self.set_auteurs_info)

        self.auteurs_dsp = QLineEdit()
        self.auteurs_dsp.setReadOnly(True)
        self.auteurs_dsp.setText(self.auteurs)
        self.auteurs_dsp.setStatusTip(" Aucune action, cette boite montre le ou les Auteur(s) protégé en écriture."
                                      " Tout ou partie du texte peut être sélectionné pour copier et coller")
                                      # No action, this box displays the the Author(s) write protected.
                                      # Part or the whole text may be selected for copy paste.

        self.auteurs_lt = QHBoxLayout()
        self.auteurs_lt.addWidget(self.auteurs_btn)
        self.auteurs_lt.addWidget(self.auteurs_dsp)

  # info boxes titre
        self.titre_btn = QPushButton("Titre", self)
        self.titre_btn.setStatusTip("Copie le Titre dans le presse-papier pour coller dans Mots-clefs à rechercher")                                   # show title
        self.titre_btn.clicked.connect(self.set_titre_info)

        self.titre_dsp = QLineEdit()
        self.titre_dsp.setReadOnly(True)
        self.titre_dsp.setText(self.titre)
        self.titre_dsp.setStatusTip(" Aucune action, cette boite montre le Titre protégé en écriture."
                                    " Tout ou partie du texte peut être sélectionné")
                                    # No action, this box displays the Title write protected.
                                    # Part or the whole text may be selected for copy paste.

        self.titre_lt = QHBoxLayout()
        self.titre_lt.addWidget(self.titre_btn)
        self.titre_lt.addWidget(self.titre_dsp)

  # search box and buttons

        self.next_btn = QPushButton('Suivant', self)
        self.next_btn.clicked.connect(self.update_searching)
        self.next_btn.setStatusTip("Cherche le suivant")
        if isinstance(self.next_btn, QPushButton): self.next_btn.clicked.connect(self.setFocus)

        self.prev_btn = QPushButton('Précédent', self)
        self.prev_btn.clicked.connect(self.find_backward)
        self.prev_btn.setStatusTip("Cherche le précédant")
        if isinstance(self.next_btn, QPushButton): self.prev_btn.clicked.connect(self.setFocus)

        self.srch_dsp = QLineEdit()
        self.srch_dsp.setStatusTip("Contient le texte a rechercher. !!! Même le charactère espace compte !!!")
        if isinstance(self.srch_dsp, QPushButton): self.srch_dsp.clicked.connect(self.setFocus)
        self.setFocusProxy(self.srch_dsp)
        self.srch_dsp.textChanged.connect(self.update_searching)
        self.srch_dsp.returnPressed.connect(self.update_searching)

        self.done_btn = QPushButton("Efface")
        self.done_btn.setStatusTip("Efface le contenu de la boite")
        self.done_btn.clicked.connect(self.srch_dsp.clear)
        if isinstance(self.done_btn, QPushButton): self.done_btn.clicked.connect(self.setFocus)

        self.srch_lt = QHBoxLayout(self)
        self.srch_lt.addWidget(self.done_btn)
        self.srch_lt.addWidget(self.srch_dsp)
        self.srch_lt.addWidget(self.next_btn)
        self.srch_lt.addWidget(self.prev_btn)


        QShortcut(QKeySequence.FindNext, self, activated=self.next_btn.animateClick)        # simule un click de souris de .1 secondes
        QShortcut(QKeySequence.FindPrevious, self, activated=self.prev_btn.animateClick)

  # put all that together center and size it
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addLayout(self.isbn_lt)
        layout.addLayout(self.auteurs_lt)
        layout.addLayout(self.titre_lt)
        layout.addLayout(self.srch_lt)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.resize(1200,1000)

  # set navigation toolbar
        nav_tb = QToolBar("Navigation")
        nav_tb.setIconSize(QSize(20,20))
        self.addToolBar(nav_tb)

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

        home_btn = QAction(get_icons('blue_icon/home.png'), "Home", self)
        home_btn.setStatusTip("On va à la recherche avancée de noosfere")           # We go to the front page of noosfere
        home_btn.triggered.connect(self.navigate_home)
        nav_tb.addAction(home_btn)

        stop_btn = QAction(get_icons('blue_icon/stop.png'), "Stop", self)
        stop_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        stop_btn.triggered.connect(self.browser.stop)
        nav_tb.addAction(stop_btn)

        self.urlbox = QLineEdit()
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.urlbox.setStatusTip("Tu peut même introduire une adresse, hors noosfere, mais A TES RISQUES ET PERILS... noosfere est sûr (https://), la toile par contre...")
                                # You can even enter an address, outside of noosfere, but AT YOUR OWN RISK... noosfere is safe: (https://), the web on the other side...
        nav_tb.addWidget(self.urlbox)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadStarted.connect(self.loading_title)
        self.browser.loadProgress.connect(self.reloading_title)
        self.browser.loadFinished.connect(self.update_title)

        abort_btn = QAction(get_icons('blue_icon/abort.png'), "Abort", self)
        abort_btn.setStatusTip("On arrête tout, on oublie tout et on ne change rien")
                              # Stop everything, forget everything and change nothing
        abort_btn.triggered.connect(self.close)             # may need another slot for abort this book , proceed next
        nav_tb.addAction(abort_btn)

        exit_btn = QAction(get_icons('blue_icon/exit.png'), "Select and exit", self)
        exit_btn.setStatusTip("On sélectionne cet URL pour extraction de nsfr_id, on continue")
                             # select this URL for extraction of nsfr_id, continue
        exit_btn.triggered.connect(self.select_and_exit)
        nav_tb.addAction(exit_btn)

  # set status bar
        self.setStatusBar(QStatusBar(self))

  # make all that visible

        self.show()

 # search action
    @pyqtSlot()
    def update_searching(self, direction=QWebEnginePage.FindFlag()):
        flag = direction
        text = self.srch_dsp.text()
        def callback(found):
            if text and not found:
                self.statusBar().showMessage('Désolé, je ne trouve pas "'+str(text)+'" plus court peut-être?')
        self.browser.findText(text, flag, callback)

    @pyqtSlot()
    def find_backward(self):
        self.update_searching(QWebEnginePage.FindBackward)

  # info boxes actions
    @pyqtSlot()
    def set_isbn_info(self):
        self.isbn_dsp.setText(self.isbn)
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(self.isbn, mode=self.cb.Clipboard)

    @pyqtSlot()
    def set_auteurs_info(self):
        self.auteurs_dsp.setText(self.auteurs)
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(self.auteurs, mode=self.cb.Clipboard)

    @pyqtSlot()
    def set_titre_info(self):
        self.titre_dsp.setText(self.titre)
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(self.titre, mode=self.cb.Clipboard)

  # Navigation actions
    def initial_url(self, url="http://www.google.com"):
        self.browser.setUrl(QUrl(url))

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://www.noosfere.org/livres/noosearch.asp"))

    def navigate_to_url(self):                    # Does not receive the Url
        q = QUrl(self.urlbox.text())
        self.browser.setUrl(q)

    def update_urlbar(self, q):
        self.urlbox.setText(q.toString())
        self.urlbox.setCursorPosition(0)

    def loading_title(self):
        title="En téléchargement de l'url"
        self.setWindowTitle(title)

    def reloading_title(self,i):
        title="En téléchargement de l'url "+i*"°"
        self.setWindowTitle(title)

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def select_and_exit(self):                    #sent response over the clipboard then exit this book
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(self.urlbox.text(), mode=self.cb.Clipboard)
        qApp.quit()     # exit application

    def closeEvent(self, event):                  # abort hit window exit "X" button
        qDebug('MainWindow.closeEvent()')
        reply = QMessageBox.question(self, 'Vraiment', "Quitter et ne plus rien changer", QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            self.cb.clear(mode=self.cb.Clipboard)
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
