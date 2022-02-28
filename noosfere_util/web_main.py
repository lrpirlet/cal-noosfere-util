#!/usr/bin/env python
# vim:fileencoding=utf-8

__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

from PyQt5.QtCore import pyqtSlot, QUrl, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QToolBar, QAction, QLineEdit, QStatusBar,
                                QMessageBox, qApp, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QShortcut)   #, QApplication, QDockWidget)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from calibre.gui2 import Application

from json import dumps
from functools import partial
import tempfile, os, sys, logging, contextlib, glob


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

class Search_Panel(QWidget):
    searched = pyqtSignal(str, QWebEnginePage.FindFlag)
    closed = pyqtSignal()

    def __init__(self,parent=None):
        super(Search_Panel,self).__init__(parent)

        self.case_btn = QPushButton('Match &Case', checkable=True)
        self.case_btn.clicked.connect(self.update_searching)
        if isinstance(self.case_btn, QPushButton): self.case_btn.clicked.connect(self.setFocus)

        next_btn = QPushButton('&Next')
        next_btn.clicked.connect(self.update_searching)
        if isinstance(next_btn, QPushButton): next_btn.clicked.connect(self.setFocus)

        prev_btn = QPushButton('&Previous')
        prev_btn.clicked.connect(self.on_preview_find)
        if isinstance(prev_btn, QPushButton): prev_btn.clicked.connect(self.setFocus)

        done_btn = QPushButton("&Done")
        done_btn.clicked.connect(self.closed)
        if isinstance(done_btn, QPushButton): done_btn.clicked.connect(self.setFocus)

        self.srch_dsp = QLineEdit()
        if isinstance(self.srch_dsp, QPushButton): self.srch_dsp.clicked.connect(self.setFocus)
        self.setFocusProxy(self.srch_dsp)
        self.srch_dsp.textChanged.connect(self.update_searching)
        self.srch_dsp.returnPressed.connect(self.update_searching)
        self.closed.connect(self.srch_dsp.clear)

        self.srch_lt = QHBoxLayout(self)
        self.srch_lt.addWidget(self.case_btn)
        self.srch_lt.addWidget(self.srch_dsp)
        self.srch_lt.addWidget(next_btn)
        self.srch_lt.addWidget(prev_btn)
        self.srch_lt.addWidget(done_btn)

        QShortcut(QKeySequence.FindNext, self, activated=next_btn.animateClick)
        QShortcut(QKeySequence.FindPrevious, self, activated=prev_btn.animateClick)
        QShortcut(QKeySequence(Qt.Key_Escape), self.srch_dsp, activated=self.closed)

    @pyqtSlot()
    def on_preview_find(self):
        self.update_searching(QWebEnginePage.FindBackward)

    @pyqtSlot()
    def update_searching(self, direction=QWebEnginePage.FindFlag()):
        flag = direction
        if self.case_btn.isChecked():
            flag |= QWebEnginePage.FindCaseSensitively
        self.searched.emit(self.srch_dsp.text(), flag)

    def showEvent(self, event):
        super(Search_Panel, self).showEvent(event)
        self.setFocus(True)

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

        self.set_browser()
        self.set_isbn_box()
        self.set_auteurs_box()
        self.set_titre_box()
        self.set_search_bar()
        self.join_all_boxes()
        self.set_nav_and_status_bar()

      # make all that visible... I want this window on top ready to work with
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()

      # signals
        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadStarted.connect(self.loading_title)
        self.browser.loadProgress.connect(self.reloading_title)
        self.browser.loadFinished.connect(self.update_title)
        self.isbn_btn.clicked.connect(partial(self.set_noosearch_page, "isbn"))
        self.auteurs_btn.clicked.connect(partial(self.set_noosearch_page, "auteurs"))
        self.titre_btn.clicked.connect(partial(self.set_noosearch_page, "titre"))

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
        self.titre_dsp = QLineEdit()
        self.titre_dsp.setReadOnly(True)
        self.titre_dsp.setText(self.titre)
        self.titre_dsp.setToolTip(" Cette boite montre le Titre protégé en écriture. Tout ou partie du texte peut être sélectionné pour chercher dans la page")
                                    # This box displays the Title write protected. Some text may be selected here to search the page.
        self.titre_lt = QHBoxLayout()
        self.titre_lt.addWidget(self.titre_btn)
        self.titre_lt.addWidget(self.titre_dsp)

  # search bar hidden when inactive ready to find something (I hope :-) )
    def set_search_bar(self):
        self.search_pnl = Search_Panel()
        self.search_toolbar = QToolBar()
        self.search_toolbar.addWidget(self.search_pnl)
        self.addToolBar(Qt.BottomToolBarArea, self.search_toolbar)
        self.search_toolbar.hide()
        self.search_pnl.searched.connect(self.on_searched)
        self.search_pnl.closed.connect(self.search_toolbar.hide)

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

        find_btn = QAction(get_icons('blue_icon/search.png'), "Search", self)
        find_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        find_btn.triggered.connect(self.wake_search_panel)
        find_btn.setShortcut(QKeySequence.Find)
        nav_tb.addAction(find_btn)

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

  # set status bar
        self.setStatusBar(QStatusBar(self))

  # search action
    @pyqtSlot(str, QWebEnginePage.FindFlag)
    def on_searched(self, text, flag):
        def callback(found):
            if text and not found:
                self.statusBar().show()
                self.statusBar().showMessage('Not found')
            else:
                self.statusBar().hide()
        self.browser.findText(text, flag, callback)

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
    def wake_search_panel(self):
        self.search_toolbar.show()

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

    def report_returned_id(self, returned_id):
        tfp=open(os.path.join(tempfile.gettempdir(),"report_returned_id"),"w")
        tfp.write(returned_id)
        tfp.close

    def select_and_exit(self):                    # sent response over report_returned_id file in temp dir
      # create a temp file with name starting with nsfr_id
        choosen_url = self.urlbox.text()
        if "numlivre=" in choosen_url:
            print('choosen_url : ',choosen_url)
            nsfr_id = "vl$"+choosen_url.split("numlivre=")[1]
            print("nsfr_id : ", nsfr_id)
            self.report_returned_id(nsfr_id)
        else:
            print('No book selected, no change will take place: unset')
            self.report_returned_id("unset")
        qApp.quit()     # exit application

    def closeEvent(self, event):                  # abort hit window exit "X" button
        reply = QMessageBox.question(self, 'Vraiment', "Quitter et ne plus rien changer", QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            print("WebEngineView was either aborted or closed: killed")
            self.report_returned_id("killed")
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
    print("glob.glob : ", glob.glob(os.path.join(tempfile.gettempdir(),"Xvl$*")))
    # cb = Application.clipboard()
    # print(cb.text(mode=cb.Clipboard))
    # choosen_url = cb.text(mode=cb.Clipboard)
    # cb.clear(mode=cb.Clipboard)

    # if "numlivre=" in choosen_url:
    #     print('choosen_url from clipboard',choosen_url)
    #     nsfr_id = "vl$"+choosen_url.split("numlivre=")[1]
    #     print("nsfr_id : ", nsfr_id)
    # else:
    #     print('no change will take place...')