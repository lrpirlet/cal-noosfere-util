from multiprocessing import Process, Queue
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import sys

class MainWindow(QMainWindow):

    def __init__(self, url, que):
        super(MainWindow,self).__init__()

        self.que = que

        self.browser = QWebEngineView()
#        self.browser.setGeometry(100, 100, 1200, 800)
        self.browser.resize(1200,800)
        self.browser.setUrl(QUrl(url))

        self.setCentralWidget(self.browser)

        get_tb = QToolBar("Get")
        get_tb.setIconSize(QSize(60,30))
        self.addToolBar(Qt.BottomToolBarArea, get_tb)

        ISBN_btn = QAction(QIcon('./blue_icon/ISBN.png'), "ISBN", self)
        ISBN_btn.setStatusTip("Montre et copie le ISBN pour coller dans Mots-clefs à rechercher")
        ISBN_btn.triggered.connect(self.navigate_home)
        get_tb.addAction(ISBN_btn)

        Auteurs_btn = QAction(QIcon('./blue_icon/Auteurs.png'), "Auteur(s)", self)
        Auteurs_btn.setStatusTip("Montre et copie le(s) Auteur(s) pour coller dans Mots-clefs à rechercher")
        Auteurs_btn.triggered.connect(self.browser.back)
        get_tb.addAction(Auteurs_btn)

        Titre_btn = QAction(QIcon('./blue_icon/Titre.png'), "Titre", self)
        Titre_btn.setStatusTip("Montre le Titre")
        Titre_btn.triggered.connect(self.browser.forward)
        get_tb.addAction(Titre_btn)

        self.getbar = QLineEdit()
        self.getbar.setReadOnly(True)
        self.getbar.setStatusTip("Aucune action, montre l'ISBN, le(s) Auteur(s) ou le Titre, protégé en écriture")
                                # No action displays the ISBN the Author(s) or the Title, in write protect
        get_tb.addWidget(self.getbar)

        nav_tb = QToolBar("Navigation")
        nav_tb.setIconSize(QSize(20,20))
        self.addToolBar(nav_tb)

        home_btn = QAction(QIcon('./blue_icon/home.png'), "Home", self)
        home_btn.setStatusTip("On va à la une de noosfere")                         # We go to the front page of noosfere
        home_btn.triggered.connect(self.navigate_home)
        nav_tb.addAction(home_btn)

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

        stop_btn = QAction(QIcon('./blue_icon/stop.png'), "Stop", self)
        stop_btn.setStatusTip("On arrête de charger la page")                       # Stop loading the page
        stop_btn.triggered.connect(self.browser.stop)
        nav_tb.addAction(stop_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.urlbar.setStatusTip("Tu peut même introduire une adresse, hors noosfere, mais A TES RISQUES ET PERILS... noosfere est sûr ( https:// ), la toile par contre...")
                                # You can even enter an address, outside of noosfere, but AT YOUR OWN RISK... noosfere is safe: ( https:// ), the web on the other side...
        nav_tb.addWidget(self.urlbar)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)

        abort_btn = QAction(QIcon('./blue_icon/abort.png'), "Abort", self)
        abort_btn.setStatusTip("On arrête tout, on oublie tout et on ne change rien")
                              # Stop everything, forget everything and change nothing
        abort_btn.triggered.connect(self.close)
        nav_tb.addAction(abort_btn)

        exit_btn = QAction(QIcon('./blue_icon/exit.png'), "Select and exit", self)
        exit_btn.setStatusTip("On sélectionne cet URL pour extraction de nsfr_id, on continue")
                             # select this URL for extraction of nsfr_id, continue
        exit_btn.triggered.connect(self.select_and_exit)
        nav_tb.addAction(exit_btn)

        self.show()

        self.setStatusBar(QStatusBar(self))

    def navigate_home(self):
        self.browser.setUrl( QUrl("https://www.noosfere.org/") )

    def navigate_to_url(self):                    # Does not receive the Url
        q = QUrl( self.urlbar.text() )
        self.browser.setUrl(q)
        print("In navigate_to_url  URL : ", self.urlbar.text())

    def update_urlbar(self, q):
        self.urlbar.setText( q.toString() )
        self.urlbar.setCursorPosition(0)

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def select_and_exit(self):                    #sent q to the queue wait till consumed then exit
        self.que.put(self.urlbar.text())
        sys.exit(0)

    def closeEvent(self, event):                  # hit window exit "X" button
        qDebug('MainWindow.closeEvent()')
        reply = QMessageBox.question(self, 'Vraiment', "Quitter et ne rien changer", QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        qDebug('MainWindow.closeEvent()'+str(reply))
        if reply == QMessageBox.Yes:
            event.accept()
            self.que.put("")
            super().closeEvent(event)
        else:
            event.ignore()

def spawned_main(que, url):
#    logfile = open("spanlog.txt", "a")
#    txt=time.strftime("%D %H:%M:%S", time.localtime())+' logfile is open now'
#    logfile.write(txt+"\n")
#    logfile.flush()
#    print(time.strftime("%D %H:%M:%S", time.localtime()), "In spawned_main(que, url)", type(que), type(url))
    app = QApplication([])
#    window = MainWindow(logfile, url, que)
    window = MainWindow(url, que)
    app.exec_()

if __name__ == '__main__':
    url="https://www.noosfere.org/livres/noosearch.asp"
    que = Queue()
    prc = Process(target=spawned_main, args=(que, url))
    prc.start()
    response = que.get()
    print("In main, la dernier url est: ", response, "len",  len(response), "type", type(response))
    prc.join()

