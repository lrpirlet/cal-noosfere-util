#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

from typing import Collection
from calibre import prints
from calibre.constants import DEBUG
from calibre.ebooks.metadata.meta import set_metadata
from calibre.gui2 import open_url, error_dialog, info_dialog
from calibre.gui2.actions import InterfaceAction, menu_action_unique_name
from calibre.utils.config import config_dir
from calibre.utils.date import UNDEFINED_DATE

#from calibre_plugins.noosfere_util.main import NoosfereUtilDialog
#from calibre_plugins.noosfere_util.common_utils import (create_menu_action_unique)

#from pkg_resources import FileMetadata
from PyQt5.Qt import QInputDialog
from PyQt5.QtWidgets import QToolButton, QMenu, QMessageBox, QApplication
from PyQt5.QtCore import qDebug, QUrl
from time import sleep

import tempfile, glob, os, contextlib

def create_menu_action_unique(ia, parent_menu, menu_text, image=None, tooltip=None,
                       shortcut=None, triggered=None, is_checked=None, shortcut_name=None,
                       unique_name=None, favourites_menu_unique_name=None):
    '''
    Create a menu action with the specified criteria and action, using the new
    InterfaceAction.create_menu_action() function which ensures that regardless of
    whether a shortcut is specified it will appear in Preferences->Keyboard
    '''

    # extracted from common_utils.py, found in many plugins ... header as follow:
    #
    # __license__   = 'GPL v3'
    # __copyright__ = '2011, Grant Drake <grant.drake@gmail.com>
    # __docformat__ = 'restructuredtext en'
    #
    # change to notice is the use of get_icons instead of get_icon in:
    #    ac.setIcon(get_icons(image))
    # ok, to be honest I could make this one work... I had lots of
    # difficulties with the many common_utils.py files that have the same name
    # but different content...
    # P.S. I like blue icons :-)...

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

    name = 'noosfere util'

    action_spec = ("noosfere util", None,
            "lance les utilités pour noosfere DB", None)
    popup_type = QToolButton.InstantPopup
    action_add_menu = True
    action_type = 'current'
    current_instance = None

  # remove previous log files for web_main process in the temp dir
    with contextlib.suppress(FileNotFoundError): os.remove(os.path.join(tempfile.gettempdir(), 'nsfr_utl-web_main.log'))
  # remove help file that may have been updated anyway
    with contextlib.suppress(FileNotFoundError): os.remove(os.path.join(tempfile.gettempdir(), "nfsr_utl_doc.html"))

    def genesis(self):
      # get_icons and get_resources are partially defined function (zip location is defined)
      # those are known when genesis is called by calibre
        icon = get_icons('blue_icon/top_icon.png')
      # qaction is created and made available by calibre for noosfere_util
        self.qaction.setIcon(icon)
      # here we create a menu in calibre
        self.build_menus()

    def build_menus(self):
        self.menu = QMenu(self.gui)
        self.menu.clear()
        create_menu_action_unique(self, self.menu, _('Efface les metadonnées en surplus'), 'blue_icon/wipe_it.png',
                                  triggered=self.wipe_selected_metadata)
        self.menu.addSeparator()

        create_menu_action_unique(self, self.menu, _('Navigateur Web pour le choix du volume'), 'blue_icon/choice.png',
                                  triggered=self.run_web_main)
        self.menu.addSeparator()

        create_menu_action_unique(self, self.menu, _("Distribue l'information éditeur"), 'blue_icon/eclate.png',
                                  triggered=self.unscramble_publisher)
        self.menu.addSeparator()

        create_menu_action_unique(self, self.menu, _("Personnalise l'extension")+'...', 'blue_icon/config.png',
                                  triggered=self.show_configuration)
        self.menu.addSeparator()

        create_menu_action_unique(self, self.menu, _('Help'), 'blue_icon/documentation.png',
                                  triggered=self.show_help)
        create_menu_action_unique(self, self.menu, _('About'), 'blue_icon/about.png',
                                  triggered=self.about)
        self.menu.addSeparator()
        create_menu_action_unique(self, self.menu, _('testtesttest'), 'blue_icon/top_icon.png',
                                  triggered=self.testtesttest)

        self.gui.keyboard.finalize()

      # Assign our menu to this action and an icon, also add dropdown menu
        self.qaction.setMenu(self.menu)

    def run_web_main(self):
        '''
        For the selected books:
        wipe metadata, launch a web-browser to select the desired volumes,
        set the nsfr_id, remove the ISBN (?fire a metadata download?)
        '''
        if DEBUG: prints("in run_web_main")

      # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Pas de métadonnée affectée',
                             'Aucun livre selectionné', show=True)

      # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        if DEBUG : prints("ids : ", ids)

      # do the job for one book
      # nsfr_id_recu is true if metadata was updated, false if web_returned no nsfr_id
        nbr_ok = 0
        set_ok = set()
        for book_id in ids:
            answer = self.run_one_web_main(book_id)
            nsfr_id_recu, more = answer[0], answer[1]
      # mark books that have NOT been bypassed... so we can fetch metadata on selected
            if nsfr_id_recu:
                nbr_ok += 1
                set_ok.add(book_id)
                prints("set_ok", set_ok)
            if not more: break

        if DEBUG: prints('nfsr_id is recorded, metadata is prepared for {} book(s) out of {}'.format(nbr_ok, len(ids)))
        info_dialog(self.gui, 'nsfr_id: enregistré',
                'Les metadonées ont été préparées pour {} livre(s) sur {}'.format(nbr_ok, len(ids)),
                show=True)
      # new_api does not know anything about marked books, so we use the full db object
        if len(set_ok):
            self.gui.current_db.set_marked_ids(set_ok)
            self.gui.search.setEditText('marked:true')
            self.gui.search.do_search()

    def run_one_web_main(self, book_id):
        '''
        For the books_id:
        wipe metadata, launch a web-browser to select the desired volumes,
        set the nsfr_id, remove the ISBN (?fire a metadata download?)
        '''
        if DEBUG: prints("in run_one_web_main")

        db = self.gui.current_db.new_api
        mi = db.get_metadata(book_id, get_cover=False, cover_as_data=False)
        isbn, auteurs, titre="","",""

        if DEBUG: prints("book_id          : ", book_id)
        if DEBUG and mi.title: prints("title       *    : ", mi.title)
        if DEBUG and mi.authors: prints("authors     *    : ", mi.authors)
        if DEBUG and "isbn" in mi.get_identifiers(): prints("isbn             : ", mi.get_identifiers()["isbn"])

      # set url, isbn, auteurs and titre
        url = "https://www.noosfere.org/livres/noosearch.asp"     # jump directly to noosfere advanced search page
        if "isbn" in mi.get_identifiers(): isbn = mi.get_identifiers()["isbn"]
        auteurs = " & ".join(mi.authors)
        titre = mi.title
        data = [url, isbn, auteurs, titre]
        if DEBUG:
            prints(" url is a string : ", isinstance(url, str))
            prints(" isbn is a string : ", isinstance(isbn, str))
            prints(" auteurs is a string : ", isinstance(auteurs, str))
            prints(" titre is a string : ", isinstance(titre, str))

      # remove all trace of an old synchronization file between calibre and the outside process running QWebEngineView
        for i in glob.glob( os.path.join(tempfile.gettempdir(),"sync-cal-qweb*")):
            with contextlib.suppress(FileNotFoundError): os.remove(i)

      # Launch a separate process to view the URL in WebEngine
        self.gui.job_manager.launch_gui_app('webengine-dialog', kwargs={'module':'calibre_plugins.noosfere_util.web_main', 'data':data})
        if DEBUG: prints("webengine-dialog process submitted")
        # WARNING: "webengine-dialog" is a defined function in calibre\src\calibre\utils\ipc\worker.py ...DO NOT CHANGE...

        # sleep some like 5 seconds to wait for web_main.py to settle and create a temp file to synchronize QWebEngineView with calibre...
        # make sure that main loop is NOT responding while QWebEngineView is running.
        # That could result in hang... on purpose, I am NOT looking for control-c...
        # that should raise attention AND trigger looking into temp dir for nsfr_utl-web_main.log
        sleep(5)

      # wait till file is removed but loop fast enough for a user to feel the operation instantaneous
        while glob.glob(os.path.join(tempfile.gettempdir(),"sync-cal-qweb*")):
            sleep(.2)           # loop fast enough for a user to feel the operation instantaneous

      # synch file is gone, meaning QWebEngineView process is closed so, we can collect the result
        tpf = open(os.path.join(tempfile.gettempdir(),"report_returned_id"), "r")
        returned_id = tpf.read()
        tpf.close()

        if DEBUG: prints("returned_id", returned_id)

        if returned_id.replace("vl$","").replace("-","").isnumeric():
            nsfr_id = returned_id
            # set the nsfr_is, reset most metadata...
            for key in mi.custom_field_keys():
                display_name, val, oldval, fm = mi.format_field_extended(key)
                if "coll_srl" in display_name : cstm_coll_srl_fm=fm
                if "collection" in display_name : cstm_collection_fm=fm
            mi.publisher=""
            mi.series=""
            mi.language=""
            mi.pubdate=UNDEFINED_DATE
            mi.set_identifier('nsfr_id', nsfr_id)
            mi.set_identifier('isbn', "")
            if cstm_coll_srl_fm:
                cstm_coll_srl_fm["#value#"] = ""
                mi.set_user_metadata("#coll_srl",cstm_coll_srl_fm)
            if cstm_collection_fm:
                cstm_collection_fm["#value#"] = ""
                mi.set_user_metadata("#collection",cstm_collection_fm)

            # commit the change, force reset of the above fields, leave the others alone
            db.set_metadata(book_id, mi, force_changes=True)
            return (True, True)                                 # nsfr_id received, more book
        elif "unset" in returned_id:
            if DEBUG: prints('unset, no change will take place...')
            return (False, True)                                # nsfr_id NOT received, more book
        elif "aborted" in returned_id:
            if DEBUG: prints('aborted, no change will take place...')
            return (False, True)                                # nsfr_id NOT received, more book
        elif "killed" in returned_id:
            if DEBUG: prints('killed, no change will take place...')
            return (False, False)                               # nsfr_id NOT received, NO more book
        else:
            if DEBUG: prints("should not ends here... returned_id : ", returned_id)
            return (False, False)                               # STOP everything program error

    def wipe_selected_metadata(self):
        '''
        For all selected book
        Deletes publisher, tags, series, rating, #coll_srl, #collection, and any ID
        except ISBN. All other fields are supposed to be overwritten when new matadata
        is downloaded from noosfere. ISBN will be wiped when nsfr_id is written later.
        '''
        if DEBUG: prints("in wipe_selected_metadata")

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Pas de métadonnée affectée',
                             'Aucun livre selectionné', show=True)

        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        if DEBUG : prints("ids : ", ids)

        for book_id in ids:
            db = self.gui.current_db.new_api
            # Get the current metadata for this book from the db (not any info about cover)
            mi = db.get_metadata(book_id, get_cover=False, cover_as_data=False)
            # find custom field of interest
            for key in mi.custom_field_keys():
                display_name, val, oldval, fm = mi.format_field_extended(key)
                if "coll_srl" in display_name : cstm_coll_srl_fm=fm
                if "collection" in display_name : cstm_collection_fm=fm
            # reset the metadata fields that need to be (publisher, series, language, pubdate, identifier)
            # leaving those we want to keep (isbn, autors, title) and those we know will be replaced or
            # augmented (comments, rating, tag, whatever custom columns...)
            mi.publisher=""
            mi.series=""
            mi.language=""
            mi.pubdate=UNDEFINED_DATE
            mi.set_identifier('nsfr_id', "")
            if cstm_coll_srl_fm:
                cstm_coll_srl_fm["#value#"] = ""
                mi.set_user_metadata("#coll_srl",cstm_coll_srl_fm)
            if cstm_collection_fm:
                cstm_collection_fm["#value#"] = ""
                mi.set_user_metadata("#collection",cstm_collection_fm)
            # commit changes
            db.set_metadata(book_id, mi, force_changes=True)

        if DEBUG: prints('Updated the metadata in the files of {} book(s)'.format(len(ids)))

        info_dialog(self.gui, 'Metadonnées changées',
                'Les metadonées ont été effacées pour {} livre(s)'.format(len(ids)),
                show=True)

    def unscramble_publisher(self):
        if DEBUG: prints("in unscramble_publisher")
      # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Pas de métadonnée affectée',
                             'Aucun livre selectionné', show=True)

        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        if DEBUG: prints("ids : ", ids)
        db = self.gui.current_db.new_api
        for book_id in ids:
          # Get the current metadata of interest for this book from the db
            mi = db.get_metadata(book_id, get_cover=False, cover_as_data=False)
            scrbl_dt = mi.publisher
            if scrbl_dt:
                collection, coll_srl = None, None
                if "€" in scrbl_dt: scrbl_dt, coll_srl = scrbl_dt.split("€")
                if "§" in scrbl_dt: scrbl_dt, collection = scrbl_dt.split("§")
                if DEBUG:
                    prints("collection : ", collection) if collection else prints("collection not in publisher")
                    prints("coll_srl   : ", coll_srl) if coll_srl else prints("coll_srl not in publisher")
                    prints("éditeur (scrbl_dt)   : ", scrbl_dt)
              # Set the current metadata of interest for this book in the db
                if collection: db.set_field("#collection", {book_id: collection})
                if coll_srl: db.set_field("#coll_srl", {book_id: coll_srl})
                db.set_field("publisher", {book_id: scrbl_dt})
                self.gui.iactions['Edit Metadata'].refresh_gui([book_id])

        info_dialog(self.gui, 'Information distribuée',
                "L'informationa été distribuée pour {} livre(s)".format(len(ids)),
                show=True)

    def testtesttest(self):
        if DEBUG: prints("in testtesttest")
        from calibre_plugins.noosfere_util.config import prefs
        prints("in testtesttest; prefs", prefs)

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        # prints("rows type : ", type(rows), "rows", rows) rows are selected rows in calibre
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Pas de métadonnée affectée',
                             'Aucun livre selectionné', show=True)

        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        prints("ids : ", ids)
        db = self.gui.current_db.new_api
        for book_id in ids:
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            fmts = db.formats(book_id)
            prints("fmts = db.formats(book_id)", fmts)
            prints(20*"*.")
            prints("book_id             : ", book_id)
            prints("mi.title       *    : ", mi.title)
            prints("mi.authors     *    : ", mi.authors)
            prints("mi.publisher   --   : ", mi.publisher)
            prints("mi.pubdate          : ", mi.pubdate)
            prints("mi.uuid             : ", mi.uuid)
            prints("mi.languages        : ", mi.languages)
            prints("mi.tags        --   : ", mi.tags)
            prints("mi.series      --   : ", mi.series)
            prints("mi.rating      --   : ", mi.rating)
            prints("mi.application_id   : ", mi.application_id)
            prints("mi.id               : ", mi.id)
            prints("mi.user_categories  : ", mi.user_categories)
            prints("mi.identifiers      : ", mi.identifiers)

            for key in mi.custom_field_keys():
                prints("custom_field_keys   : ", key)
            prints(20*"#²")

            for key in mi.custom_field_keys():
                #prints("custom_field_keys   : ", key)
                display_name, val, oldval, fm = mi.format_field_extended(key)
                #prints("display_name=%s, val=%s, oldval=%s, ff=%s" % (display_name, val, oldval, fm))
                if fm and fm['datatype'] != 'composite':
                    prints("custom_field_keys not composite : ", key)
                    #prints("display_name=%s, val=%s, oldval=%s, ff=%s" % (display_name, val, oldval, fm))
                    prints("display_name : ", display_name)
                    # prints("fm : ", fm)
                    for key in fm:
                        prints("fm keys : ", key, end="      | " )
                        prints("fm[{}] : ".format(key), fm[key])
                    prints(20*"..")
                if "coll_srl" in display_name : cstm_coll_srl_fm=fm
                if "collection" in display_name : cstm_collection_fm=fm

            prints(20*"+-")
            prints("#coll_srl           : ", db.field_for('#coll_srl', book_id))
            prints("#collection         : ", db.field_for('#collection', book_id))

            mi.publisher=""
            mi.series=""
            mi.language=""
            mi.set_identifier('nsfr_id', "")

            if cstm_coll_srl_fm:
                cstm_coll_srl_fm["#value#"] = ""
                mi.set_user_metadata("#coll_srl",cstm_coll_srl_fm)
            if cstm_collection_fm:
                cstm_collection_fm["#value#"] = ""
                mi.set_user_metadata("#collection",cstm_collection_fm)

            # db.set_metadata(book_id, mi, force_changes=True)


        info_dialog(self.gui, 'Updated files',
                'Updated the metadata in the files of {} book(s)'.format(len(ids)),
                show=True)

    def show_configuration(self):
        '''
        will present the configuration widget... should handle custom columns needed for
        #collection and #coll_srl
        '''
        if DEBUG: prints("in show_configuration")

        self.interface_action_base_plugin.do_user_config(self.gui)

    def show_help(self):
         # Extract on demand the help file resource to a temp file
        def get_help_file_resource():
          # keep "nfsr_utl_doc.html" as the last item in the list, this is the help entry point
          # we need both files for the help
            file_path = os.path.join(tempfile.gettempdir(), "nfsr_utl_doc.html")
            file_data = self.load_resources('doc/' + "nfsr_utl_doc.html")['doc/' + "nfsr_utl_doc.html"]
            if DEBUG: prints('show_help - file_path:', file_path)
            with open(file_path,'wb') as f:
                f.write(file_data)
            return file_path
        url = 'file:///' + get_help_file_resource()
        url = QUrl(url)
        open_url(url)

    def about(self):
        text = get_resources("doc/about.txt")
        QMessageBox.about(self.gui, 'About the Interface Plugin Demo',
                text.decode('utf-8'))

    def apply_settings(self):
        from calibre_plugins.noosfere_util.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        if DEBUG: prints("in apply_settings")
        if DEBUG: prints("prefs", prefs)        # prefs is a dict {}
        prefs
