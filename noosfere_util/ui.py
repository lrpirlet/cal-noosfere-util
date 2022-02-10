#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from PyQt5.Qt import QInputDialog
from PyQt5.QtWidgets import QApplication
from time import sleep

import tempfile
import glob
import os

#from multiprocessing import Queue
# https://docs.python.org/fr/3/library/multiprocessing.html?highlight=queue#multiprocessing.Queue

class InterfacePlugin(InterfaceAction):

    name = 'noosfere utilités'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ("noosfere utilités", None,
            "lance les utilités pour noosfere DB", None)

    def genesis(self):
        # This method is called once per plugin, do initial setup here

        # Set the icon for this interface action
        # The get_icons function is a builtin function defined for all your
        # plugin code. It loads icons from the plugin zip file. It returns
        # QIcon objects, if you want the actual data, use the analogous
        # get_resources builtin function.
        #
        # Note that if you are loading more than one icon, for performance, you
        # should pass a list of names to get_icons. In this case, get_icons
        # will return a dictionary mapping names to QIcons. Names that
        # are not found in the zip file will result in null QIcons.
        icon = get_icons('blue_icon/top_icon.png')

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):

        # Ask the user for a URL
        #url, ok = QInputDialog.getText(self.gui, 'Enter a URL', 'Enter a URL to browse below', text='https://www.noosfere.org/livres/editionslivre.asp?numitem=7385 ')
        #if not ok or not url:
        #   return
        # set url, isbn, auteurs and titre
        url="https://www.noosfere.org/livres/noosearch.asp"
        isbn = "2266027646"
        auteurs = "Philip José Farmer"
        titre = "L'Odyssée verte"
        data = [url, isbn, auteurs, titre]

        # remove all trace of an old synchronization file between calibre and the outside process running QWebEngineView
        for i in glob.glob( os.path.join(tempfile.gettempdir(),"sync-cal-qweb*")):
            os.remove(i)

        # initialize clipboard so no old data will pollute results
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)

        # Launch a separate process to view the URL in WebEngine
        self.gui.job_manager.launch_gui_app('webengine-dialog', kwargs={'module':'calibre_plugins.noosfere_util.web_main', 'data':data})
        # WARNING: "webengine-dialog" is a defined function in calibre\src\calibre\utils\ipc\worker.py ...DO NOT CHANGE...

        # sleep some like 5 seconds to wait for web_main.py to settle and create a temp file to synchronize QWebEngineView with calibre...
        # according to the tempfile doc, this temp file MAY be system wide... CARE if more than ONE user runs calibre
        sleep(5)                # so there is time enough to create atemp file with sync-cal-qweb prefix
        while glob.glob( os.path.join(tempfile.gettempdir(),"sync-cal-qweb*")):         # wait till file is removed
            sleep(.2)           # loop fast enough for a user to feel the operation instantaneous

        # synch file is gone, meaning QWebEngineView process is closed so, we can collect the result in the system clipboard
        print("webengine-dialog process submitted")
#        cb = QApplication.clipboard()
        print(cb.text(mode=cb.Clipboard))
        choosen_url = cb.text(mode=cb.Clipboard)
        cb.clear(mode=cb.Clipboard)

        if choosen_url:
            print('choosen_url from clipboard',choosen_url, "type(choosen_url)", type(choosen_url))
        else:
            print('no change will take place...')

        return


#     def launch_gui_app(self, name, args=(), kwargs=None, description=''):
#         job = ParallelJob(name, description, lambda x: x,
#                 args=list(args), kwargs=kwargs or {})
#         self.serverserver.run_job(job, gui=True, redirect_output=False)
#
# from jobs.py in gui2 in calibre in src...
#