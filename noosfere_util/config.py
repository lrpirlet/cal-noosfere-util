#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

# from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from calibre.gui2.ui import get_gui
from calibre.gui2.preferences.create_custom_column import CreateNewCustomColumn
from calibre.utils.config import JSONConfig
from calibre.constants import DEBUG
from calibre import prints

from functools import partial

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
        info_label = QLabel("Select the columns to expand the overloaded publisher\n")
        info_label.setFont(QFont('Arial', 12))
        info_label.setAlignment(Qt.AlignCenter)

        label_collection = QLabel("#collection name")
        self.name_collection = QComboBox(self)
        self.name_collection.addItems(self.pertinent_collection_list)
        self.name_collection.activated[str].connect(self.select_for_collection)

        label_coll_srl = QLabel("#coll_srl name")
        self.name_coll_srl = QComboBox(self)
        self.name_coll_srl.addItems(self.pertinent_coll_srl_list)
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
        if name == "Ajouter et sélectionner une colonne":
            new_name =  self.create_custom_column(lookup_name = "#collection")
            if new_name:
                if DEBUG: prints("ici on adapte le combo box et on choisi new_name : ", new_name)
        else: self.collection_name = name
        if DEBUG: prints("self.collection_name : ", self.collection_name)

    def select_for_coll_srl(self, name):
        if name == "Ajouter et sélectionner une colonne":
            new_name = self.create_custom_column(lookup_name = "#coll_srl")
            if new_name:
                if DEBUG: prints("ici on adapte le combo box et on choisi new_name : ", new_name)
        else: self.coll_srl_name = name
        if DEBUG: prints("self.coll_srl_name : ", self.coll_srl_name)


    def create_custom_column(self, lookup_name=None):
        if DEBUG: prints("create_custom_column - lookup_name:", lookup_name)
        if "#collection" in lookup_name:
            display_params = {"description": "La collection definie par l'editeur dont fait partie le volume"}
            datatype = "text"
            column_heading  = "collection"
        elif "coll_srl" in lookup_name:
            display_params = {"description": "Le code de série dans la collection de l'éditeur"}
            datatype = "comments"
            column_heading  = "coll_srl"
        new_lookup_name = lookup_name

        creator = CreateNewCustomColumn(get_gui())
        result = creator.create_column(new_lookup_name, column_heading, datatype, False, display=display_params, generate_unused_lookup_name=True, freeze_lookup_name=False)
        if result[0] == CreateNewCustomColumn.Result.COLUMN_ADDED:
            creator.must_restart = True
            return result[1]
        return ""



    def save_settings(self):
        if DEBUG: prints("in save_settings")
        if DEBUG: prints("self.collection_name : ", self.collection_name)
        if DEBUG: prints("self.coll_srl_name : ", self.coll_srl_name)

        prefs["COLLECTION_NAME"] = self.collection_name
        prefs["COLL_SRL_NAME"] = self.coll_srl_name
