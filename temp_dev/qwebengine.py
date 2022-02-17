from PyQt5.QtCore import pyqtSlot, qDebug, QUrl, QSize, Qt
from PyQt5.QtWidgets import (QMainWindow, QApplication, QToolBar, QAction, QLineEdit,
                                QStatusBar, QMessageBox, qApp, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton, QShortcut, QDockWidget)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from json import dumps
import sys

class MainWindow(QMainWindow):

    def __init__(self, data):
        super().__init__()

        # data = [url, isbn, auteurs, titre]
        self.isbn, self.auteurs, self.titre = data[1].replace("-",""), data[2], data[3]

        qDebug("isbn    : "+self.isbn)
        qDebug("auteurs : "+str(self.auteurs.encode('utf-8')))
        qDebug("titre   : "+str(self.titre.encode('utf-8')))

        self.cb = QApplication.clipboard()

        self.set_browser()
        self.set_isbn_box()
        self.set_auteurs_box()
        self.set_titre_box()
        self.join_all_boxes()
        self.set_search_box()
        self.set_search_dock()
        self.set_nav_and_status_bar()

      # make all that visible

        self.show()

      # signals

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.urlChanged.connect(self.srch_dsp.clear)
        self.browser.urlChanged.connect(self.search_dock.hide)
        self.browser.loadStarted.connect(self.loading_title)
        self.browser.loadProgress.connect(self.reloading_title)
        self.browser.loadFinished.connect(self.update_title)
        self.search_dock.visibilityChanged.connect(self.srch_dsp.clear)

    def set_browser(self):                      # browser
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))

    def set_isbn_box(self):                     # info boxes isbn
        self.isbn_btn = QPushButton(" ISBN ", self)
        self.isbn_btn.setStatusTip('Page initiale: "Mots-clefs à rechercher" = ISBN, coche la case "Livre"... Ailleur: boite de recherche = ISBN')
                                   # Home page: "Mots-clefs à rechercher" = ISBN, set checkbox "Livre"... anywhere else: search box = ISBN
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

    def set_auteurs_box(self):                  # info boxes auteurs
        self.auteurs_btn = QPushButton("Auteur(s)", self)
        self.auteurs_btn.setStatusTip('Page initiale: "Mots-clefs à rechercher" = Auteur(s), coche la case "Auteurs"... Ailleur: boite de recherche = Auteurs')
                                      # Home page: "Mots-clefs à rechercher" = Auteur(s), set checkbox "Auteurs"... anywhere else: search box = Auteurs
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

    def set_titre_box(self):                    # info boxes titre
        self.titre_btn = QPushButton("Titre", self)
        self.titre_btn.setStatusTip('Page initiale: "Mots-clefs à rechercher" = Titre, coche la case "Livres"... Ailleur: boite de recherche = Titre')
                                    # Home page: "Mots-clefs à rechercher" = Titre, set checkbox "Livres"... anywhere else: search box = Titre
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

    def set_search_box(self):                   # search box and buttons
        self.next_btn = QPushButton('Suivant', self)
        self.next_btn.clicked.connect(self.update_searching)
        self.next_btn.setStatusTip("Cherche le suivant")
        if isinstance(self.next_btn, QPushButton): self.next_btn.clicked.connect(self.setFocus)

        self.prev_btn = QPushButton('Précédent', self)
        self.prev_btn.clicked.connect(self.find_backward)
        self.prev_btn.setStatusTip("Cherche le précédant")
        if isinstance(self.prev_btn, QPushButton): self.prev_btn.clicked.connect(self.setFocus)

        self.srch_dsp = QLineEdit()
        self.srch_dsp.setStatusTip("Contient le texte a rechercher. !!! Même le charactère espace compte !!!")

        self.setFocusProxy(self.srch_dsp)
        self.srch_dsp.textChanged.connect(self.update_searching)
        self.srch_dsp.returnPressed.connect(self.update_searching)

        self.done_btn = QPushButton("Efface")
        self.done_btn.setStatusTip("Efface le contenu de la boite")
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

    def set_nav_and_status_bar(self) :          # set navigation toolbar and status bar
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
        home_btn.setStatusTip("On va à la recherche avancée de noosfere")           # We go to the front page of noosfere
        home_btn.triggered.connect(self.navigate_home)
        nav_tb.addAction(home_btn)

        stop_btn = QAction(QIcon('./blue_icon/stop.png'), "Stop", self)
        stop_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        stop_btn.triggered.connect(self.browser.stop)
        nav_tb.addAction(stop_btn)

        nav_tb.addSeparator()

        srch_btn = QAction(QIcon('./blue_icon/search.png'), "Find", self)
        srch_btn.setShortcut(QKeySequence.Find)
        srch_btn.setStatusTip("Z'avez pas vu Mirza? Oh la la la la la. Où est donc passé ce chien. Je le cherche partout...  (Merci Nino Ferrer)")                       # Stop loading the page
        srch_btn.triggered.connect(self.search_dock.show)
        nav_tb.addAction(srch_btn)

        self.urlbox = QLineEdit()
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.urlbox.setStatusTip("Tu peut même introduire une adresse, hors noosfere, mais A TES RISQUES ET PERILS... noosfere est sûr (https://), la toile par contre...")
                                # You can even enter an address, outside of noosfere, but AT YOUR OWN RISK... noosfere is safe: (https://), the web on the other side...
        nav_tb.addWidget(self.urlbox)

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

        self.setStatusBar(QStatusBar(self))


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
    def set_noosearch_page(self, html_str):
        self.html = html_str
        if self.iam == "isbn": val = self.isbn
        elif self.iam == "auteurs": val = self.auteurs
        else: val = self.titre
        self.browser.page().runJavaScript("document.getElementsByName('Mots')[1].value =" + dumps(val))
        if self.iam == "auteurs":
            self.browser.page().runJavaScript("document.getElementsByName('auteurs')[0].checked = true")
            self.browser.page().runJavaScript("document.getElementsByName('livres')[0].checked = false")
        else:
            self.browser.page().runJavaScript("document.getElementsByName('livres')[0].checked = true")
            self.browser.page().runJavaScript("document.getElementsByName('auteurs')[0].checked = false")

    @pyqtSlot()
    def set_isbn_info(self):
        if self.urlbox.text() == "https://www.noosfere.org/livres/noosearch.asp":
            self.iam = "isbn"
            self.browser.page().toHtml(self.set_noosearch_page)
        else:
            self.search_dock.show()
            self.srch_dsp.setText(isbn)

    @pyqtSlot()
    def set_auteurs_info(self):
        if self.urlbox.text() == "https://www.noosfere.org/livres/noosearch.asp":
            self.iam = "auteurs"
            self.browser.page().toHtml(self.set_noosearch_page)
        else:
            self.search_dock.show()
            self.srch_dsp.setText(auteurs)

    @pyqtSlot()
    def set_titre_info(self):
        if self.urlbox.text() == "https://www.noosfere.org/livres/noosearch.asp":
            self.iam = "titre"
            self.browser.page().toHtml(self.set_noosearch_page)
        else:
            self.search_dock.show()
            self.srch_dsp.setText(titre)

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



url="https://www.noosfere.org/livres/noosearch.asp"
isbn = "2-277-12362-5"
auteurs = "Alfred Elton VAN VOGT"
titre = "Le Monde des Ã"
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



