from multiprocessing import Process, Queue
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import sys

class MainWindow(QMainWindow):

#    def __init__(self, log, url, que):
    def __init__(self, url, que):
        super(MainWindow,self).__init__()
        
        self.que = que
#        self.log = log
#        print("In __init__,  log : ", type(log), log)
#        print("In __init__,  que : ", type(que), que)        

        self.browser = QWebEngineView()
        self.browser.setGeometry(300, 300, 1200, 800)
        self.browser.setUrl(QUrl(url))

        self.setCentralWidget(self.browser)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(20,20))
        self.addToolBar(navtb)

        home_btn = QAction(QIcon('./blue/home.png'), "home", self)
        home_btn.setStatusTip("On va à la une de noosfere")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        back_btn = QAction(QIcon('./blue/back.png'), "Back", self)
        back_btn.setStatusTip("On revient à la page précédente")
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon('./blue/forward.png'), "Forward", self)
        next_btn.setStatusTip("On retourne à la page précédente")
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)

        reload_btn = QAction(QIcon('./blue/reload.png'), "Reload", self)
        reload_btn.setStatusTip("On recharge la page")
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)
        
        stop_btn = QAction(QIcon('./blue/stop.png'), "stop", self)
        stop_btn.setStatusTip("stop loading page")
        stop_btn.triggered.connect(self.browser.stop)
        navtb.addAction(stop_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)

        exit_btn = QAction(QIcon('./blue/exit.png'), "Select and exit", self)
        exit_btn.setStatusTip("on sélectionne cet URL pour extraction de nsfr_id et on retourne à calibre")
        exit_btn.triggered.connect(self.select_and_exit)
        navtb.addAction(exit_btn)
        
        self.show()

        self.setStatusBar(QStatusBar(self))

    def navigate_home(self):
        self.browser.setUrl( QUrl("https://www.noosfere.org/") )

    def navigate_to_url(self): # Does not receive the Url
        q = QUrl( self.urlbar.text() )
        self.browser.setUrl(q)
        print("In navigate_to_url  URL : ", self.urlbar.text())

    def update_urlbar(self, q):
        self.urlbar.setText( q.toString() )
        self.urlbar.setCursorPosition(0)

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def select_and_exit(self):              #sent q to the queue wait till consumed then exit
        self.que.put(self.urlbar.text())
        sys.exit(0)

    def closeEvent(self, event):    # hit window exit "X" button
        self.que.put("window was closed")
        super().closeEvent(event)
        
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
    print("In main, la dernier url est: ", que.get())
    prc.join()
    
