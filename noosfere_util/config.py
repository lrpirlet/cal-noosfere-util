#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

# from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from calibre import prints
from calibre.constants import DEBUG
from calibre.gui2.ui import get_gui
from calibre.gui2.preferences.create_custom_column import CreateNewCustomColumn
from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/noosfere_util) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/noosfere_util')

# Set defaults
prefs.defaults["COLLECTION_NAME"] = "#collection"
prefs.defaults["COLL_SRL_NAME"] = "#coll_srl"


class ConfigWidget(QWidget):

    def __init__(self, plugin_action):
        QWidget.__init__(self)
        self.plugin_action = plugin_action

        self.collection_name = prefs.defaults["COLLECTION_NAME"]
        self.coll_srl_name = prefs.defaults["COLL_SRL_NAME"]

        self.current_collection_name = prefs["COLLECTION_NAME"]
        self.current_coll_srl_name = prefs["COLL_SRL_NAME"]
        if DEBUG:
            prints("self.current_collection_name : ", self.current_collection_name)
            prints("self.current_coll_srl_name : ", self.current_coll_srl_name)

        self.pertinent_collection_list = self.get_custom_columns("text")
        self.pertinent_coll_srl_list = self.get_custom_columns("comments")

        self.pertinent_collection_list.extend(["", "Ajouter et sélectionner une colonne"])
        self.pertinent_coll_srl_list.extend(["", "Ajouter et sélectionner une colonne"])

        self.setGeometry(100, 100, 300, 200)

        self.pick_columns_name()
        if DEBUG:
            prints("get_custom_columns type: text (for collection): ", self.get_custom_columns("text"))
            prints("get_custom_columns type: comments  (for coll_srl): ", self.get_custom_columns("comments"))
        self.show()

    def get_custom_columns(self, column_type):
        """
        return a list of column suitable for column_type
          (either "comment": column not shown in the Tag browser,
          or "text": column shown in the Tag browser)
        """
        if DEBUG: prints("In get_custom_columns(self, {})".format(column_type))
        custom_columns = self.plugin_action.gui.library_view.model().custom_columns
        # if DEBUG: prints("In get_custom_columns; custom_columns : {})".format(custom_columns))
        possible_columns = []
        for key, column in custom_columns.items():
            typ = column['datatype']
            if typ in column_type and not column['is_multiple']:
                possible_columns.append(key)
        if DEBUG: prints("In get_custom_columns; possible_columns :", possible_columns)
        return sorted(possible_columns)

    def pick_columns_name(self):
        """
        Create the widgets so users can select or create a column from the combo boxes
        """
        info_label = QLabel("Sélectionne les colonnes pour l'information surchargée éditeur")
        info_label.setFont(QFont('Arial', 12))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setToolTip("En selectionnant la creation de colonne on redémare calibre. Ensuite, apres le redémarage, on poura selectionner une colonne valide.")

        label_collection = QLabel("#collection name")
        label_collection.setToolTip("La colonne présentée est celle actuellement selectionnée.")
        self.name_collection = QComboBox(self)
        self.name_collection.addItems(self.pertinent_collection_list)
        self.name_collection.setCurrentIndex(self.name_collection.findText(self.current_collection_name,Qt.MatchFixedString))
        self.name_collection.activated[str].connect(self.select_for_collection)

        label_coll_srl = QLabel("#coll_srl name")
        self.name_coll_srl = QComboBox(self)
        label_coll_srl.setToolTip("La colonne présentée est celle actuellement selectionnée.")
        self.name_coll_srl.addItems(self.pertinent_coll_srl_list)
        self.name_coll_srl.setCurrentIndex(self.name_coll_srl.findText(self.current_coll_srl_name,Qt.MatchFixedString))
        self.name_coll_srl.activated[str].connect(self.select_for_coll_srl)
      # First line
        h_box1 = QHBoxLayout()
        h_box1.addWidget(label_collection)
        h_box1.addWidget(self.name_collection)
      # Second line
        h_box2 = QHBoxLayout()
        h_box2.addWidget(label_coll_srl)
        h_box2.addWidget(self.name_coll_srl)
      # Add widgets and layouts to QVBoxLayout
        v_box = QVBoxLayout()
        v_box.addWidget(info_label)
        v_box.addLayout(h_box1)
        v_box.addLayout(h_box2)
      # v_box.addWidget(self.display_total_label)
        self.setLayout(v_box)

    def select_for_collection(self, name):
        new_name=None
        if name == "Ajouter et sélectionner une colonne":
            allow_restart = QMessageBox.question(self, 'On devra redémarer calibre',
                    "Cette action va céer une colonne valide pour contenir la collection definie par l'editeur dont fait partie le volume. "
                    "Elle pourra etre selectionée apres le redémarage...\n"
                    "On crée la colonne?",
                        QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
            if allow_restart == QMessageBox.Yes:
                self.create_custom_column(lookup_name = "#collection")
            # if new_name:
            #     if DEBUG: prints("ici on adapte le combo box et on choisi new_name : ", new_name)
            #     self.name_collection.addItems([new_name])
            #     self.collection_name = new_name
            #     self.name_collection.setCurrentIndex(self.name_collection.findText(new_name,Qt.MatchFixedString))
            # else:
            #     self.collection_name = self.current_collection_name
            #     self.name_collection.setCurrentIndex(self.name_collection.findText(self.current_collection_name,Qt.MatchFixedString))
        else:
            self.collection_name = name
            self.name_collection.setCurrentIndex(self.name_collection.findText(name,Qt.MatchFixedString))
        if DEBUG: prints("self.collection_name : ", self.collection_name)

    def select_for_coll_srl(self, name):
        new_name=None
        if name == "Ajouter et sélectionner une colonne":
            allow_restart = QMessageBox.question(self, 'On devra redémarer calibre',
                    "Cette action va céer une colonne valide pour contenir le code de série dans la collection de l'éditeur. "
                    "Elle pourra etre selectionée apres le redémarage...\n"
                    "On crée la colonne?",
                        QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
            if allow_restart == QMessageBox.Yes:
                self.create_custom_column(lookup_name = "#coll_srl")
            # if new_name:
            #     if DEBUG: prints("ici on adapte le combo box et on choisi new_name : ", new_name)
            #     self.name_coll_srl.addItems([new_name])
            #     self.coll_srl_name = new_name
            #     self.name_coll_srl.setCurrentIndex(self.name_coll_srl.findText(new_name,Qt.MatchFixedString))
            # else:
            #     self.coll_srl_name = name
            #     self.name_coll_srl.setCurrentIndex(self.name_coll_srl.findText(self.current_coll_srl_name,Qt.MatchFixedString))
        else:
            self.coll_srl_name = name
            self.name_coll_srl.setCurrentIndex(self.name_coll_srl.findText(name,Qt.MatchFixedString))
        if DEBUG: prints("self.coll_srl_name : ", self.coll_srl_name)


    def create_custom_column(self, lookup_name=None):
        if DEBUG: prints("create_custom_column - lookup_name:", lookup_name)
        if "#collection" in lookup_name:
            display_params = {"description": "La collection definie par l'editeur dont fait partie le volume"}
            datatype = "text"
            column_heading  = "collection"
        elif "coll_srl" in lookup_name:
            display_params =   {'description': "Le code de série dans la collection de l'éditeur", 'heading_position': 'hide', 'interpret_as': 'short-text'}
            datatype = "comments"
            column_heading  = "coll_srl"
        new_lookup_name = lookup_name

        creator = CreateNewCustomColumn(get_gui())
        if DEBUG:
            prints("creator : ", creator)
            prints("type(creator) : ", type(creator))
        if creator.must_restart():
            restart = QMessageBox.question(self, 'Désolé, faut redémarer calibre avant de continuer',
                                "Aucune modification ne peut plus etre actée... "
                                "Redémarer maintenant, avant de créer une autre colonne ?",
                                    QMessageBox.Abort | QMessageBox.Yes, QMessageBox.Yes)
            if restart == QMessageBox.Yes:
                self.save_settings
                get_gui().quit(restart=True)
            else:
                return ""

        result = creator.create_column(new_lookup_name, column_heading, datatype, False, display=display_params, generate_unused_lookup_name=True, freeze_lookup_name=False)
        if DEBUG: prints("result : ", result)
        if result[0] == CreateNewCustomColumn.Result.COLUMN_ADDED:
            get_gui().quit(restart=True)
            # return result[1]
        return ""



    def save_settings(self):
        if DEBUG: prints("in save_settings")
        if DEBUG: prints("self.collection_name : ", self.collection_name)
        if DEBUG: prints("self.coll_srl_name : ", self.coll_srl_name)

        prefs["COLLECTION_NAME"] = self.collection_name
        prefs["COLL_SRL_NAME"] = self.coll_srl_name
