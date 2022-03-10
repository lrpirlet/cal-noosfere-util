#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2021, Louis Richard Pirlet'

# from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from calibre.utils.config import JSONConfig
from calibre import prints

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/noosfere_util) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/noosfere_util')

# Set defaults
prefs.defaults['hello_world_msg'] = 'Hello, World!'


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.initializeUI()

    def initializeUI(self):
        """
        Initialize the window and display its contents to the screen
        """
        # self.setGeometry(100, 100, 300, 200)
        # self.setWindowTitle('ComboBox and SpinBox')
        self.columns_name()
        self.show()

    def columns_name(self):
        """
        Create the widgets so users can select or create a column from the combo boxes
        """
        info_label = QLabel("Select the columns to expand the overloaded publisher")
        info_label.setFont(QFont('Arial', 12))
        info_label.setAlignment(Qt.AlignCenter)

        lunch_list = ["egg", "turkey sandwich", "ham sandwich", "cheese", "hummus", "yogurt", "apple", "banana", "orange", "waffle", "baby carrots", "bread", "pasta", "crackers", "pretzels", "pita chips", "coffee", "soda", "water"]

        label_collection = QLabel("#collection name")
        self.name_collection = QComboBox(self)
        self.name_collection.addItems(lunch_list)
        self.name_collection.activated[str].connect(self.onSelected)

        label_coll_srl = QLabel("#coll_srl name")
        name_coll_srl = QComboBox(self)
        name_coll_srl.addItems(lunch_list)

        h_box1 = QHBoxLayout()
        h_box2 = QHBoxLayout()
        h_box1.addWidget(label_collection)
        h_box1.addWidget(self.name_collection)
        h_box2.addWidget(label_coll_srl)
        h_box2.addWidget(name_coll_srl)
        # Add widgets and layouts to QVBoxLayout
        v_box = QVBoxLayout()
        v_box.addWidget(info_label)
        v_box.addLayout(h_box1)
        v_box.addLayout(h_box2)
        # v_box.addWidget(self.display_total_label)
        self.setLayout(v_box)

    def onSelected(self, txtVal):

        txtVal = "\nYou have selected: " + txtVal

        prints(txtVal)


    # def __init__(self):
    #     QWidget.__init__(self)
    #     self.l = QHBoxLayout()
    #     self.setLayout(self.l)

    #     self.label = QLabel('Hello world &message:')
    #     self.l.addWidget(self.label)

    #     self.msg = QLineEdit(self)
    #     self.msg.setText(prefs['hello_world_msg'])
    #     self.l.addWidget(self.msg)
    #     self.label.setBuddy(self.msg)

    def save_settings(self):
        # prefs['hello_world_msg'] = self.msg.text()
        prefs['hello_world_msg'] = "Hello LRP"
