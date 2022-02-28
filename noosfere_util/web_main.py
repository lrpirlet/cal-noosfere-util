#!/usr/bin/env python
# vim:fileencoding=utf-8

__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

from PyQt5.QtCore import pyqtSlot, qDebug, QUrl, QSize, Qt
from PyQt5.QtWidgets import (QMainWindow, QToolBar, QAction, QLineEdit, QDockWidget,
                                QMessageBox, qApp, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QShortcut)   #, QApplication, QStatusBar)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from calibre.gui2 import Application
from calibre.utils.config import config_dir

from json import dumps
from functools import partial
import tempfile
import os
import sys
import logging

# faut voir le suivant....
# 1 utiliser confirm() ???
#from calibre.gui2.dialogs.confirm_delete import confirm
#    def delete_user_categories(self):
#        if not confirm(
#            _('All user categories will be deleted. Are you sure you want to proceed?'),
#            'category_tags_delete_all_categories'):
#            return
# 2 QApplication ou Application ???

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    This will help when the web browser in web_main does not pop-up (read: web_main crashes)
    """
    def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

    def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()

class MainWindow(QMainWindow):
    """
    this process, running in the calibre environment, is detached from calibre program
    It does receive data from noofere_util, processes it, then communicates back the result and dies.
    In fact this is a WEB browser centered on www.noosfere.org to get the nsfr_id of a choosen volume.

    """

    def __init__(self, data):
        super().__init__()

        # data = [url, isbn, auteurs, titre]
        self.isbn, self.auteurs, self.titre = data[1].replace("-",""), data[2], data[3]

        self.cb = Application.clipboard()

        self.set_browser()
        self.set_isbn_box()
        self.set_auteurs_box()
        self.set_titre_box()
        self.join_all_boxes()
        self.set_search_box()
        self.set_search_dock()
        self.set_nav_and_status_bar()

      # make all that visible... I want this window on top ready to work with
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()

      # signals
        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.urlChanged.connect(self.srch_dsp.clear)
        self.browser.urlChanged.connect(self.search_dock.hide)
        self.browser.loadStarted.connect(self.loading_title)
        self.browser.loadProgress.connect(self.reloading_title)
        self.browser.loadFinished.connect(self.update_title)
        self.search_dock.visibilityChanged.connect(self.srch_dsp.clear)
        self.isbn_btn.clicked.connect(partial(self.set_noosearch_page, "isbn"))
        self.auteurs_btn.clicked.connect(partial(self.set_noosearch_page, "auteurs"))
        self.titre_btn.clicked.connect(partial(self.set_noosearch_page, "titre"))
        self.isbn_dsp.selectionChanged.connect(partial(self.find_selected, "isbn"))
        self.auteurs_dsp.selectionChanged.connect(partial(self.find_selected, "auteurs"))
        self.titre_dsp.selectionChanged.connect(partial(self.find_selected, "titre"))

      # browser
    def set_browser(self):
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))

      # info boxes
    def set_isbn_box(self):                     # info boxes isbn
        self.isbn_btn = QPushButton(" ISBN ", self)
        self.isbn_btn.setToolTip('Action sur la page initiale: "Mots-clefs à rechercher" = ISBN, coche la case "Livre".')
                                   # Action on home page: "Mots-clefs à rechercher" = ISBN, set checkbox "Livre".
        self.isbn_dsp = QLineEdit()
        self.isbn_dsp.setReadOnly(True)
        self.isbn_dsp.setText(self.isbn)
        self.isbn_dsp.setToolTip(" Cette boite montre l'ISBN protégé en écriture. Du texte peut y être sélectionné pour chercher dans la page")
                                   # This box displays the ISBN write protected. Some text may be selected here to search the page.

        self.isbn_lt = QHBoxLayout()
        self.isbn_lt.addWidget(self.isbn_btn)
        self.isbn_lt.addWidget(self.isbn_dsp)

    def set_auteurs_box(self):                  # info boxes auteurs
        self.auteurs_btn = QPushButton("Auteur(s)", self)
        self.auteurs_btn.setToolTip('Action sur la page initiale: "Mots-clefs à rechercher" = Auteur(s), coche la case "Auteurs".')
                                      # Action on home page: "Mots-clefs à rechercher" = Auteur(s), set checkbox "Auteurs".
        self.auteurs_dsp = QLineEdit()
        self.auteurs_dsp.setReadOnly(True)
        self.auteurs_dsp.setText(self.auteurs)
        self.auteurs_dsp.setToolTip(" Cette boite montre le ou les Auteur(s) protégé en écriture. Du texte peut être sélectionné pour chercher dans la page")
                                      # This box displays the Author(s) write protected. Some text may be selected here to search the page.
        self.auteurs_lt = QHBoxLayout()
        self.auteurs_lt.addWidget(self.auteurs_btn)
        self.auteurs_lt.addWidget(self.auteurs_dsp)

    def set_titre_box(self):                    # info boxes titre
        self.titre_btn = QPushButton("Titre", self)
        self.titre_btn.setToolTip('Action sur la page initiale: "Mots-clefs à rechercher" = Titre, coche la case "Livres".')
                                    # Action on home page: "Mots-clefs à rechercher" = Titre, set checkbox "Livres".
        # self.titre_btn.clicked.connect(self.set_titre_info)
        self.titre_dsp = QLineEdit()
        self.titre_dsp.setReadOnly(True)
        self.titre_dsp.setText(self.titre)
        self.titre_dsp.setToolTip(" Cette boite montre le Titre protégé en écriture. Tout ou partie du texte peut être sélectionné pour chercher dans la page")
                                    # This box displays the Title write protected. Some text may be selected here to search the page.
        self.titre_lt = QHBoxLayout()
        self.titre_lt.addWidget(self.titre_btn)
        self.titre_lt.addWidget(self.titre_dsp)

    def join_all_boxes(self):                   # put all that together, center, size and make it central widget
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addLayout(self.isbn_lt)
        layout.addLayout(self.auteurs_lt)
        layout.addLayout(self.titre_lt)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.resize(1200,1000)

      # search box and buttons
    def set_search_box(self):
        self.next_btn = QPushButton('Suivant', self)
        self.next_btn.clicked.connect(self.update_searching)
        self.next_btn.setToolTip("Cherche le suivant")
        if isinstance(self.next_btn, QPushButton): self.next_btn.clicked.connect(self.setFocus)

        self.prev_btn = QPushButton('Précédent', self)
        self.prev_btn.clicked.connect(self.find_backward)
        self.prev_btn.setToolTip("Cherche le précédant")
        if isinstance(self.prev_btn, QPushButton): self.prev_btn.clicked.connect(self.setFocus)

        self.srch_dsp = QLineEdit()
        self.srch_dsp.setToolTip("Contient le texte a rechercher. !!! Même le charactère espace compte !!!")

        self.setFocusProxy(self.srch_dsp)
        self.srch_dsp.textChanged.connect(self.update_searching)
        self.srch_dsp.returnPressed.connect(self.update_searching)

        self.done_btn = QPushButton("Efface")
        self.done_btn.setToolTip("Efface le contenu de la boite")
        self.done_btn.clicked.connect(self.srch_dsp.clear)
        if isinstance(self.done_btn, QPushButton): self.done_btn.clicked.connect(self.setFocus)

        QShortcut(QKeySequence.FindNext, self, activated=self.next_btn.animateClick)
        QShortcut(QKeySequence.FindPrevious, self, activated=self.prev_btn.animateClick)

    def set_search_dock(self):                  # build a dockable windows
        self.search_dock = QDockWidget("Fenêtre de recherche")
        self.search_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.search_dock_content = QWidget()

        srch_lt = QHBoxLayout()
        srch_lt.addWidget(self.next_btn)
        srch_lt.addWidget(self.prev_btn)
        srch_lt.addWidget(self.srch_dsp)
        srch_lt.addWidget(self.done_btn)


        self.search_dock_content.setLayout(srch_lt)
        self.search_dock.setWidget(self.search_dock_content)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.search_dock)
        self.search_dock.hide()

      # set navigation toolbar
    def set_nav_and_status_bar(self) :
        nav_tb = QToolBar("Navigation")
        nav_tb.setIconSize(QSize(20,20))
        self.addToolBar(nav_tb)

        back_btn = QAction(get_icons('blue_icon/back.png'), "Back", self)
        back_btn.setToolTip("On revient à la page précédente")                    # Back to the previous page
        back_btn.triggered.connect(self.browser.back)
        nav_tb.addAction(back_btn)

        next_btn = QAction(get_icons('blue_icon/forward.png'), "Forward", self)
        next_btn.setToolTip("On retourne à la page suivante")                     # Back to the next page
        next_btn.triggered.connect(self.browser.forward)
        nav_tb.addAction(next_btn)

        reload_btn = QAction(get_icons('blue_icon/reload.png'), "Reload", self)
        reload_btn.setToolTip("On recharge la page")                              # Reload the page
        reload_btn.triggered.connect(self.browser.reload)
        nav_tb.addAction(reload_btn)

        home_btn = QAction(get_icons('blue_icon/home.png'), "Home", self)
        home_btn.setToolTip("On va à la recherche avancée de noosfere")           # We go to the front page of noosfere
        home_btn.triggered.connect(self.navigate_home)
        nav_tb.addAction(home_btn)

        stop_btn = QAction(get_icons('blue_icon/stop.png'), "Stop", self)
        stop_btn.setToolTip("On arrête de charger la page")                       # Stop loading the page
        stop_btn.triggered.connect(self.browser.stop)
        nav_tb.addAction(stop_btn)

        nav_tb.addSeparator()

        srch_btn = QAction(get_icons('blue_icon/search.png'), "Find", self)
        srch_btn.setShortcut(QKeySequence.Find)
        srch_btn.setToolTip("Z'avez pas vu Mirza? Oh la la la la la. Où est donc passé ce chien. Je le cherche partout...  (Merci Nino Ferrer)")                       # Stop loading the page
        srch_btn.triggered.connect(self.search_dock.show)
        nav_tb.addAction(srch_btn)

        self.urlbox = QLineEdit()
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.urlbox.setToolTip("Tu peut même introduire une adresse, hors noosfere, mais A TES RISQUES ET PERILS... noosfere est sûr (https://), la toile par contre...")
                                # You can even enter an address, outside of noosfere, but AT YOUR OWN RISK... noosfere is safe: (https://), the web on the other side...
        nav_tb.addWidget(self.urlbox)

        abort_btn = QAction(get_icons('blue_icon/abort.png'), "Abort", self)
        abort_btn.setToolTip("On arrête tout, on oublie tout et on ne change rien")
                              # Stop everything, forget everything and change nothing
        abort_btn.triggered.connect(self.close)             # may need another slot for abort this book , proceed next
        nav_tb.addAction(abort_btn)

        exit_btn = QAction(get_icons('blue_icon/exit.png'), "Select and exit", self)
        exit_btn.setToolTip("On sélectionne cet URL pour extraction de nsfr_id, on continue")
                             # select this URL for extraction of nsfr_id, continue
        exit_btn.triggered.connect(self.select_and_exit)
        nav_tb.addAction(exit_btn)

  # search action
    @pyqtSlot()
    def update_searching(self, direction=QWebEnginePage.FindFlag()):
        flag = direction
        text = self.srch_dsp.text()
        def callback(found):
            if text and not found:
                self.statusBar().showMessage('Désolé, je ne trouve pas "'+str(text)+'" plus court peut-être?')
        self.browser.findText(text, flag) #, callback)

    @pyqtSlot()
    def find_backward(self):
        self.update_searching(QWebEnginePage.FindBackward)

  # info boxes actions
    @pyqtSlot()
    def set_noosearch_page(self, iam):
        if self.urlbox.text() == "https://www.noosfere.org/livres/noosearch.asp":
            if iam == "isbn": val = self.isbn
            elif iam == "auteurs": val = self.auteurs
            else: val = self.titre
            self.browser.page().runJavaScript("document.getElementsByName('Mots')[1].value =" + dumps(val))
            if iam == "auteurs":
                self.browser.page().runJavaScript("document.getElementsByName('auteurs')[0].checked = true")
                self.browser.page().runJavaScript("document.getElementsByName('livres')[0].checked = false")
            else:
                self.browser.page().runJavaScript("document.getElementsByName('livres')[0].checked = true")
                self.browser.page().runJavaScript("document.getElementsByName('auteurs')[0].checked = false")
        else:
            pass
    
    @pyqtSlot()
    def find_selected(self, iam):
        self.search_dock.show()
        if iam == "isbn": slctd = self.isbn_dsp.selectedText()
        elif iam == "auteurs": slctd = self.auteurs_dsp.selectedText()
        elif iam == "titre": slctd = self.titre_dsp.selectedText()
        self.srch_dsp.setText(slctd)

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
        self.srch_dsp.clear()
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(self.urlbox.text(), mode=self.cb.Clipboard)
        qApp.quit()     # exit application

    def closeEvent(self, event):                  # abort hit window exit "X" button
        qDebug('MainWindow.closeEvent()')
        reply = QMessageBox.question(self, 'Vraiment', "Quitter et ne plus rien changer", QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            self.srch_dsp.clear()
            self.cb.clear(mode=self.cb.Clipboard)
            super().closeEvent(event)
        else:
            event.ignore()


def main(data):

    # Initialize environment..
    # note: web_main is NOT supposed to output anything over STDOUT or STDERR

    logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename = os.path.join(tempfile.gettempdir(), 'nsfr_utl-web_main.log'),
    filemode = 'a')

    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl

    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

    # create a temp file... while it exists launcher program will wait... this file will disappear with the process
    tfp=tempfile.NamedTemporaryFile(prefix="sync-cal-qweb")


    # retrieve component from data
    #        data = [url, isbn, auteurs, titre]
    url, isbn, auteurs, titre = data[0], data[1], data[2], data[3],

    # Start QWebEngineView and associated widgets
    app = Application([])
    window = MainWindow(data)
    window.initial_url(url)     # supposed to be noosfere advanced search page, fixed by launcher program
    app.exec()

    # signal launcher program that we are finished
    tfp.close           # close temp file


if __name__ == '__main__':
    '''
    watch out name 'get_icons' is not defined, and can't be defined really... 
    workaround, swap it with QIcon + path to icon
    '''
    url = "https://www.noosfere.org/livres/noosearch.asp"   # jump directly to noosfere advanced search page
    isbn = "2-277-12362-5"
    auteurs = "Alfred Elton VAN VOGT"                       # forget not that auteurs may be a list of auteurs
    titre = "Le Monde des Ã"
    data = [url, isbn, auteurs, titre]
    main(data)
    cb = Application.clipboard()
    print(cb.text(mode=cb.Clipboard))
    choosen_url = cb.text(mode=cb.Clipboard)
    cb.clear(mode=cb.Clipboard)

    if "numlivre=" in choosen_url:
        print('choosen_url from clipboard',choosen_url)
        nsfr_id = "vl$"+choosen_url.split("numlivre=")[1]
        print("nsfr_id : ", nsfr_id)
    else:
        print('no change will take place...')