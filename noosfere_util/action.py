#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

# if False:
#     # This is here to keep my python error checker from complaining about
#     # the builtin functions that will be defined by the plugin loading system
#     # You do not need this code in your plugins
#     get_icons = get_resources = None

# The class that all interface action plugins must inherit from
from calibre import prints
from calibre.constants import DEBUG
from calibre.utils.config import config_dir
from calibre.gui2.actions import menu_action_unique_name

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import open_url

from calibre_plugins.noosfere_util.main import NoosfereUtilDialog
#from calibre_plugins.noosfere_util.common_utils import (create_menu_action_unique)

from PyQt5.Qt import QInputDialog
from PyQt5.QtWidgets import QToolButton, QMenu, QMessageBox
from PyQt5.QtCore import qDebug, QUrl
from time import sleep

import tempfile
import glob
import os

#from multiprocessing import Queue
# https://docs.python.org/fr/3/library/multiprocessing.html?highlight=queue#multiprocessing.Queue

# extracted from common_utils.py, found in many plugin,s ... header as follow:
# __license__   = 'GPL v3'
# __copyright__ = '2011, Grant Drake <grant.drake@gmail.com>
# __docformat__ = 'restructuredtext en'
# only change is the use of get_icons instead of get_icon in:
#    ac.setIcon(get_icons(image))
# I like blue icons :-)

def create_menu_action_unique(ia, parent_menu, menu_text, image=None, tooltip=None,
                       shortcut=None, triggered=None, is_checked=None, shortcut_name=None,
                       unique_name=None, favourites_menu_unique_name=None):
    '''
    Create a menu action with the specified criteria and action, using the new
    InterfaceAction.create_menu_action() function which ensures that regardless of
    whether a shortcut is specified it will appear in Preferences->Keyboard
    '''
    orig_shortcut = shortcut
    kb = ia.gui.keyboard
    if unique_name is None:
        unique_name = menu_text
    if not shortcut == False:
        full_unique_name = menu_action_unique_name(ia, unique_name)
        if full_unique_name in kb.shortcuts:
            shortcut = False
        else:
            if shortcut is not None and not shortcut == False:
                if len(shortcut) == 0:
                    shortcut = None
                else:
                    shortcut = _(shortcut)

    if shortcut_name is None:
        shortcut_name = menu_text.replace('&','')

    ac = ia.create_menu_action(parent_menu, unique_name, menu_text, icon=None, shortcut=shortcut,
        description=tooltip, triggered=triggered, shortcut_name=shortcut_name)
    if shortcut == False and not orig_shortcut == False:
        if ac.calibre_shortcut_unique_name in ia.gui.keyboard.shortcuts:
            kb.replace_action(ac.calibre_shortcut_unique_name, ac)
    if image:
        ac.setIcon(get_icons(image))
    if is_checked is not None:
        ac.setCheckable(True)
        if is_checked:
            ac.setChecked(True)
    return ac
    
class InterfacePlugin(InterfaceAction):

    name = 'noosfere utilités'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    # Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)

    action_spec = ("noosfere utilités", None,
            "lance les utilités pour noosfere DB", None)
    popup_type = QToolButton.InstantPopup
    action_add_menu = True
    action_type = 'current'

    current_instance = None

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

    #def initialization_complete(self):
        self.build_menus()

    # def show_dialog(self):
    #     # The base plugin object defined in __init__.py
        # base_plugin_object = self.interface_action_base_plugin
    #     # Show the config dialog
    #     # The config dialog can also be shown from within
    #     # Preferences->Plugins, which is why the do_user_config
    #     # method is defined on the base plugin class
        # do_user_config = base_plugin_object.do_user_config

    #     # self.gui is the main calibre GUI. It acts as the gateway to access
    #     # all the elements of the calibre user interface, it should also be the
    #     # parent of the dialog
    #     d = NoosfereUtilDialog(self.gui, self.qaction.icon(), do_user_config)
    #     d.show()

    def build_menus(self):
        self.menu = QMenu(self.gui)
        self.menu.clear()

        create_menu_action_unique(self, self.menu, _('Export User Categories')+'...', 'arrow-up.png',
                                  triggered=self.export_user_categories)

        create_menu_action_unique(self, self.menu, _('Import User Categories')+'...', 'arrow-down.png',
                                  triggered=self.import_user_categories)

        self.menu.addSeparator()

        create_menu_action_unique(self, self.menu, _('Delete User Categories')+'...', 'minus.png',
                                  triggered=self.delete_user_categories)

        self.menu.addSeparator()

        create_menu_action_unique(self, self.menu, _('Customize plugin')+'...', 'blue_icon/config.png',
                                  triggered=self.show_configuration)

        self.menu.addSeparator()

        #self.advanced_help_action = 
        create_menu_action_unique(self, self.menu, _('Help'), 'blue_icon/documentation.png',
                                  triggered=self.show_help)

        create_menu_action_unique(self, self.menu, _('About'), 'blue_icon/documentation.png',
                                  triggered=self.about)

        self.gui.keyboard.finalize()

        # Assign our menu to this action and an icon, also add dropdown menu
        self.qaction.setMenu(self.menu)

    def export_user_categories(self):
        qDebug("in commented-export_user_categories")

    def import_user_categories(self):
        qDebug("in commented-import_user_categories")

    def delete_user_categories(self):
        qDebug("in commented-delete_user_categories")

    def show_configuration(self):
        self.interface_action_base_plugin.do_user_config(self.gui)

    def show_help(self):
        text = get_resources("doc/doc.html").decode("utf-8")
        url = text
        url = QUrl(url)
        open_url(url)

#    def show_help(self):
#         def get_help_file_resource():
#             # Extract on demand the help file resource
#             # The help file is written out every time, in case the user upgrades the plugin zip
#             # and there is a later help file contained within it.
#             # from calibre.utils.localization import get_lang
#             # lang = get_lang()
#             #HELP_FILE = 'KoboUtilities_Help_en.html'
#             HELP_FILE = "doc.html"
#             # if lang == 'fr':
#             #     HELP_FILE = 'KoboUtilities_Help_fr.html'
#             file_path = os.path.join(config_dir, 'plugins', HELP_FILE)
#             file_data = self.load_resources('doc/' + HELP_FILE)['doc/' + HELP_FILE]
#             if DEBUG: prints('show_help - file_path:', file_path)
#             # debug_print('show_help - file_path:', file_path)
# #             if DEBUG: prints('show_help - file_data:', file_data)
# #             debug_print('show_help - file_data:', file_data)
#             with open(file_path,'wb') as f:
#                 f.write(file_data)
#             return file_path
#         url = 'file:///' + get_help_file_resource()
#         url = QUrl(url)
#         open_url(url)

    def about(self):
        text = get_resources("doc/about.txt")
        QMessageBox.about(self.gui, 'About the Interface Plugin Demo',
                text.decode('utf-8'))

    def apply_settings(self):
        from calibre_plugins.noosfere_util.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        if DEBUG: prints("in apply_settings")
        prefs

#############################################################################################################

# #!/usr/bin/env python
# # vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

# __license__   = 'GPL v3'
# __copyright__ = '2021, Louis Richard Pirlet'

# if False:
#     # This is here to keep my python error checker from complaining about
#     # the builtin functions that will be defined by the plugin loading system
#     # You do not need this code in your plugins
#     get_icons = get_resources = None

# from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
# from pkg_resources import FileMetadata

# from calibre_plugins.noosfere_util.config import prefs


# class NoosfereUtilDialog(QDialog):

#     def __init__(self, gui, icon, do_user_config):
#         QDialog.__init__(self, gui)
#         self.gui = gui
#         self.do_user_config = do_user_config

#         # The current database shown in the GUI
#         # db is an instance of the class LibraryDatabase from db/legacy.py
#         # This class has many, many methods that allow you to do a lot of
#         # things. For most purposes you should use db.new_api, which has
#         # a much nicer interface from db/cache.py
#         self.db = gui.current_db

#         self.l = QVBoxLayout()
#         self.setLayout(self.l)

#         self.label = QLabel(prefs['hello_world_msg'])
#         self.l.addWidget(self.label)

#         self.setWindowTitle('Interface Plugin Demo')
#         self.setWindowIcon(icon)

#         self.about_button = QPushButton('About', self)
#         self.about_button.clicked.connect(self.about)
#         self.l.addWidget(self.about_button)

#         self.marked_button = QPushButton(
#             'Show books with only one format in the calibre GUI', self)
#         self.marked_button.clicked.connect(self.marked)
#         self.l.addWidget(self.marked_button)

#         self.view_button = QPushButton(
#             'View the most recently added book', self)
#         self.view_button.clicked.connect(self.view)
#         self.l.addWidget(self.view_button)

#         self.update_metadata_button = QPushButton(
#             'Update metadata in a book\'s files', self)
#         self.update_metadata_button.clicked.connect(self.update_metadata)
#         self.l.addWidget(self.update_metadata_button)

#         self.update_metadata_button = QPushButton(
#             'noosfere_selected', self)
#         self.update_metadata_button.clicked.connect(self.noosfere_selected)
#         self.l.addWidget(self.update_metadata_button)

#         self.conf_button = QPushButton(
#                 'Configure this plugin', self)
#         self.conf_button.clicked.connect(self.config)
#         self.l.addWidget(self.conf_button)

#         self.resize(self.sizeHint())

    def about(self):
        # Get the about text from a file inside the plugin zip file
        # The get_resources function is a builtin function defined for all your
        # plugin code. It loads files from the plugin zip file. It returns
        # the bytes from the specified file.
        #
        # Note that if you are loading more than one file, for performance, you
        # should pass a list of names to get_resources. In this case,
        # get_resources will return a dictionary mapping names to bytes. Names that
        # are not found in the zip file will not be in the returned dictionary.
        text = get_resources("doc/about.txt")
        QMessageBox.about(self.gui, 'About the Interface Plugin Demo',
                text.decode('utf-8'))

#     def marked(self):
#         ''' Show books with only one format '''
#         db = self.db.new_api
#         matched_ids = {book_id for book_id in db.all_book_ids() if len(db.formats(book_id)) == 1}
#         # Mark the records with the matching ids
#         # new_api does not know anything about marked books, so we use the full
#         # db object
#         self.db.set_marked_ids(matched_ids)

#         # Tell the GUI to search for all marked records
#         self.gui.search.setEditText('marked:true')
#         self.gui.search.do_search()

#     def view(self):
#         ''' View the most recently added book '''
#         most_recent = most_recent_id = None
#         db = self.db.new_api
#         for book_id, timestamp in db.all_field_for('timestamp', db.all_book_ids()).items():
#             if most_recent is None or timestamp > most_recent:
#                 most_recent = timestamp
#                 most_recent_id = book_id

#         if most_recent_id is not None:
#             # Get a reference to the View plugin
#             view_plugin = self.gui.iactions['View']
#             # Ask the view plugin to launch the viewer for row_number
#             view_plugin._view_calibre_books([most_recent_id])

#     def update_metadata(self):
#         '''
#         Set the metadata in the files in the selected book's record to
#         match the current metadata in the database.
#         '''
#         from calibre.ebooks.metadata.meta import set_metadata
#         from calibre.gui2 import error_dialog, info_dialog

#         # Get currently selected books
#         rows = self.gui.library_view.selectionModel().selectedRows()
#         if not rows or len(rows) == 0:
#             return error_dialog(self.gui, 'Cannot update metadata',
#                              'No books selected', show=True)
#         # Map the rows to book ids
#         ids = list(map(self.gui.library_view.model().id, rows))
#         db = self.db.new_api
#         for book_id in ids:
#             # Get the current metadata for this book from the db
#             mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
#             fmts = db.formats(book_id)
#             if not fmts:
#                 continue
#             for fmt in fmts:
#                 fmt = fmt.lower()
#                 # Get a python file object for the format. This will be either
#                 # an in memory file or a temporary on disk file
#                 ffile = db.format(book_id, fmt, as_file=True)
#                 ffile.seek(0)
#                 # Set metadata in the format
#                 set_metadata(ffile, mi, fmt)
#                 ffile.seek(0)
#                 # Now replace the file in the calibre library with the updated
#                 # file. We dont use add_format_with_hooks as the hooks were
#                 # already run when the file was first added to calibre.
#                 db.add_format(book_id, fmt, ffile, run_hooks=False)

#         info_dialog(self, 'Updated files',
#                 'Updated the metadata in the files of %d book(s)'%len(ids),
#                 show=True)

#     def noosfere_selected(self):
#         '''
#         Set the metadata in the files in the selected book's record to
#         match the current metadata in the database.
#         '''
#         #from calibre.library import db
#         from calibre.ebooks.metadata.meta import set_metadata
#         from calibre.gui2 import error_dialog, info_dialog
#         from calibre import prints

#         prints("Entering noosfere_selected")

#         # Get currently selected books
#         rows = self.gui.library_view.selectionModel().selectedRows()
#         # prints("rows type : ", type(rows), "rows", rows) rows are selected rows in calibre
#         if not rows or len(rows) == 0:
#             return error_dialog(self.gui, 'Cannot update metadata',
#                              'No books selected', show=True)
#         # Map the rows to book ids
#         ids = list(map(self.gui.library_view.model().id, rows))
#         prints("ids : ", ids)
#         db = self.db.new_api
#         for book_id in ids:
#             # Get the current metadata for this book from the db
#             mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
#             fmts = db.formats(book_id)
#             prints("fmts = db.formats(book_id)", fmts)
#             prints(20*"*.")
#             prints("book_id             : ", book_id)
#             prints("mi.title       *    : ", mi.title)
#             prints("mi.authors     *    : ", mi.authors)
#             prints("mi.publisher   --   : ", mi.publisher)
#             prints("mi.pubdate          : ", mi.pubdate)
#             prints("mi.uuid             : ", mi.uuid)
#             prints("mi.languages        : ", mi.languages)
#             prints("mi.tags        --   : ", mi.tags)
#             prints("mi.series      --   : ", mi.series)
#             prints("mi.rating      --   : ", mi.rating)
#             prints("mi.application_id   : ", mi.application_id)
#             prints("mi.id               : ", mi.id)
#             prints("mi.user_categories  : ", mi.user_categories)
#             prints("mi.identifiers      : ", mi.identifiers)

#             for key in mi.custom_field_keys():
#                 prints("custom_field_keys   : ", key)
#             prints(20*"#²")

#             for key in mi.custom_field_keys():
#                 #prints("custom_field_keys   : ", key)
#                 display_name, val, oldval, fm = mi.format_field_extended(key)
#                 #prints("display_name=%s, val=%s, oldval=%s, ff=%s" % (display_name, val, oldval, fm))
#                 if fm and fm['datatype'] != 'composite':
#                     prints("custom_field_keys not composite : ", key)
#                     prints("display_name=%s, val=%s, oldval=%s, ff=%s" % (display_name, val, oldval, fm))
#                     prints(20*"..")
#                 if "coll_srl" in display_name : cstm_coll_srl_fm=fm
#                 if "collection" in display_name : cstm_collection_fm=fm

#             prints(20*"+-")
#             prints("#collection         : ", db.field_for('#collection', book_id))

#             mi.publisher=""
#             mi.series=""
#             mi.language=""
#             mi.set_identifier('nsfr_id', "")

#             cstm_coll_srl_fm["#value#"] = ""
#             mi.set_user_metadata("#coll_srl",cstm_coll_srl_fm)

#             cstm_collection_fm["#value#"] = ""
#             mi.set_user_metadata("#collection",cstm_collection_fm)

#             db.set_metadata(book_id, mi, force_changes=True)


#         info_dialog(self, 'Updated files',
#                 'Updated the metadata in the files of %d book(s)'%len(ids),
#                 show=True)

#     def config(self):
#         self.do_user_config(parent=self)
#         # Apply the changes
#         self.label.setText(prefs['hello_world_msg'])


#############################################################################################################
##def show_dialog(self):
##
##        # Ask the user for a URL
##        #url, ok = QInputDialog.getText(self.gui, 'Enter a URL', 'Enter a URL to browse below', text='https://www.noosfere.org/livres/editionslivre.asp?numitem=7385 ')
##        #if not ok or not url:
##        #   return
##        # set url, isbn, auteurs and titre
##        book_id = ""
##        isbn = "2266027646"
##        auteurs = "Philip José Farmer"
##        titre = "L'Odyssée verte"
##        data = [book_id, isbn, auteurs, titre]
##
##        # remove all trace of an old synchronization file between calibre and the outside process running QWebEngineView
##        for i in glob.glob( os.path.join(tempfile.gettempdir(),"sync-cal-qweb*")):
##            os.remove(i)
##
##        # initialize clipboard so no old data will pollute results
##        cb = QApplication.clipboard()
##        cb.clear(mode=cb.Clipboard)
##
##        # Launch a separate process to view the URL in WebEngine
##        self.gui.job_manager.launch_gui_app('webengine-dialog', kwargs={'module':'calibre_plugins.noosfere_util.web_main', 'data':data})
##        # WARNING: "webengine-dialog" is a defined function in calibre\src\calibre\utils\ipc\worker.py ...DO NOT CHANGE...
##
##        # sleep some like 5 seconds to wait for web_main.py to settle and create a temp file to synchronize QWebEngineView with calibre...
##        # according to the tempfile doc, this temp file MAY be system wide... CARE if more than ONE user runs calibre
##        sleep(5)                # so there is time enough to create atemp file with sync-cal-qweb prefix
##        while glob.glob( os.path.join(tempfile.gettempdir(),"sync-cal-qweb*")):         # wait till file is removed
##            sleep(.2)           # loop fast enough for a user to feel the operation instantaneous
##
##        # synch file is gone, meaning QWebEngineView process is closed so, we can collect the result in the system clipboard
##        print("webengine-dialog process submitted")
###        cb = QApplication.clipboard()
##        print(cb.text(mode=cb.Clipboard))
##        choosen_url = cb.text(mode=cb.Clipboard)
##        cb.clear(mode=cb.Clipboard)
##
##        if choosen_url:
##            print('choosen_url from clipboard',choosen_url, "type(choosen_url)", type(choosen_url))
##        else:
##            print('no change will take place...')
##
##        return
##
##
###     def launch_gui_app(self, name, args=(), kwargs=None, description=''):
###         job = ParallelJob(name, description, lambda x: x,
###                 args=list(args), kwargs=kwargs or {})
###         self.serverserver.run_job(job, gui=True, redirect_output=False)
###
### from jobs.py in gui2 in calibre in src...
###
