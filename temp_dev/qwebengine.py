from PyQt5.QtCore import pyqtSlot, qDebug, QUrl, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QApplication, QToolBar, QAction, QLineEdit, 
                                QStatusBar, QMessageBox, qApp, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton, QShortcut)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import sys
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

        QShortcut(QKeySequence.FindNext, self, activated=next_btn.animateClick)        # simule un click de souris de .1 secondes
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
    def __init__(self, data):
        super().__init__()

        # data = [url, isbn, auteurs, titre]
        self.isbn, self.auteurs, self.titre = data[1].replace("-",""), data[2], data[3]

        qDebug("isbn    : "+self.isbn)
        qDebug("auteurs : "+str(self.auteurs.encode('utf-8')))
        qDebug("titre   : "+str(self.titre.encode('utf-8')))

        self.cb = QApplication.clipboard()

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
        self.titre_btn.setStatusTip("Montre le Titre")                                   # show title
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

  # search bar hidden when inactive ready to find something (I hope :-) )
        self.search_pnl = Search_Panel()
        self.search_toolbar = QToolBar()
        self.search_toolbar.addWidget(self.search_pnl)
        self.addToolBar(Qt.BottomToolBarArea, self.search_toolbar)
        self.search_toolbar.hide()
        self.search_pnl.searched.connect(self.on_searched)
        self.search_pnl.closed.connect(self.search_toolbar.hide)

  # put all that together center and size it
        layout = QVBoxLayout()
        layout.addWidget(self.browser)        
        layout.addLayout(self.isbn_lt)
        layout.addLayout(self.auteurs_lt)
        layout.addLayout(self.titre_lt)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.resize(1200,950)

  # set navigation toolbar
        nav_tb = QToolBar("Navigation")
        nav_tb.setIconSize(QSize(20,20))
        self.addToolBar(nav_tb)

        back_btn = QAction(QIcon('./blue_icon/back.png'), "Back", self)
        back_btn.setStatusTip("On revient à la page précédente")                    # Back to the previous page
        back_btn.triggered.connect(self.browser.back)
        nav_tb.addAction(back_btn)

        next_btn = QAction(QIcon('./blue_icon/forward.png'), "Forward", self)
        next_btn.setStatusTip("On retourne à la page suivante")                     # Back to the next page
        next_btn.triggered.connect(self.browser.forward)
        nav_tb.addAction(next_btn)

        reload_btn = QAction(QIcon('./blue_icon/reload.png'), "Reload", self)
        reload_btn.setStatusTip("On recharge la page")                              # Reload the page
        reload_btn.triggered.connect(self.browser.reload)
        nav_tb.addAction(reload_btn)

        home_btn = QAction(QIcon('./blue_icon/home.png'), "Home", self)
        home_btn.setStatusTip("On va à la recherche avancée de noosfere")                         # We go to the front page of noosfere
        home_btn.triggered.connect(self.navigate_home)
        nav_tb.addAction(home_btn)

        stop_btn = QAction(QIcon('./blue_icon/stop.png'), "Stop", self)
        stop_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        stop_btn.triggered.connect(self.browser.stop)
        nav_tb.addAction(stop_btn)

        find_btn = QAction(QIcon('./blue_icon/search.png'), "Search", self)
        find_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        find_btn.triggered.connect(self.wake_search_panel)
        find_btn.setShortcut(QKeySequence.Find)
        nav_tb.addAction(find_btn)

        self.urlbox = QLineEdit()
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.urlbox.setStatusTip("Tu peut même introduire une adresse, hors noosfere, mais A TES RISQUES ET PERILS... noosfere est sûr (https://), la toile par contre...")
                                # You can even enter an address, outside of noosfere, but AT YOUR OWN RISK... noosfere is safe: (https://), the web on the other side...
        nav_tb.addWidget(self.urlbox)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadStarted.connect(self.loading_title)
        self.browser.loadProgress.connect(self.reloading_title)
        self.browser.loadFinished.connect(self.update_title)

        abort_btn = QAction(QIcon('./blue_icon/abort.png'), "Abort", self)
        abort_btn.setStatusTip("On arrête tout, on oublie tout et on ne change rien")
                              # Stop everything, forget everything and change nothing
        abort_btn.triggered.connect(self.close)             # may need another slot for abort this book , proceed next
        nav_tb.addAction(abort_btn)

        exit_btn = QAction(QIcon('./blue_icon/exit.png'), "Select and exit", self)
        exit_btn.setStatusTip("On sélectionne cet URL pour extraction de nsfr_id, on continue")
                             # select this URL for extraction of nsfr_id, continue
        exit_btn.triggered.connect(self.select_and_exit)
        nav_tb.addAction(exit_btn)

  # set status bar
        self.setStatusBar(QStatusBar(self))

  # make all that visible

        self.show()

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



url="https://www.noosfere.org/livres/noosearch.asp"
isbn = "2-277-12362-5"
auteurs = "Alfred Elton VAN VOGT"
titre = "Un tres tres long titre qui n'a rien a voir avec l'auteur ou l'ISBN... Le Monde des Ã"
data = [url, isbn, auteurs, titre]
app = QApplication([])
window = MainWindow(data)
window.initial_url(url)
app.exec_()                 # allows remaining instructions to be executed
#sys.exit(app.exec_())      # to debug sys.exit() will output message about the error

cb = QApplication.clipboard()
print(cb.text(mode=cb.Clipboard))
choosen_url = cb.text(mode=cb.Clipboard)
cb.clear(mode=cb.Clipboard)

if "numlivre=" in choosen_url:
    print('choosen_url from clipboard',choosen_url)
    nsfr_id = "vl$"+choosen_url.split("numlivre=")[1]
    print("nsfr_id : ", nsfr_id)
else:
    print('no change will take place...')


