#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import QWidget, QCheckBox, QGridLayout, QVBoxLayout, QGroupBox, QComboBox, QLabel, QButtonGroup
except ImportError:
    from PyQt4.Qt import QWidget, QCheckBox, QGridLayout, QVBoxLayout, QGroupBox, QComboBox, QLabel, QButtonGroup

from calibre.utils.config import JSONConfig
from calibre_plugins.EmbedComicMetadata.setup import get_configuration, CONFIG_NAME, CONFIG_TITLE, CONFIG_DEFAULT, CONFIG_COLUMN_TYPE


# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/EmbedComicMetadata')

config = get_configuration()

# set defaults
for group in config:
    for item in group["Items"]:
        prefs.defaults[item[CONFIG_NAME]] = item[CONFIG_DEFAULT]


class ConfigWidget(QWidget):

    def __init__(self, ia):
        QWidget.__init__(self)
        self.ia = ia
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        # make the config menu
        for group in config:
            self.make_submenu(group)

        # make menu button choices exclusive
        self.make_exclusive("exclusive_group", [self.main_embed, self.main_import])

    def save_settings(self):
        for group in config:
            if group["Type"] == "columnboxes":
                func = self.CustomColumnComboBox.get_selected_column
            if group["Type"] == "checkboxes":
                func = QCheckBox.isChecked
            for item in group["Items"]:
                action = getattr(self, item[CONFIG_NAME])
                prefs[item[CONFIG_NAME]] = func(action)
        # rebuild the menu
        self.ia.toggle_menu_items()

    def make_submenu(self, cfg):
        lo = self.make_groupbox(cfg["Name"] + "_box", cfg["Title"], self.l)
        i, k = 1, 0
        for item in cfg["Items"]:
            # make the element
            if cfg["Type"] == "checkboxes":
                self.make_checkbox(item[CONFIG_NAME], item[CONFIG_TITLE],
                    prefs[item[CONFIG_NAME]], lo, i, k)
            if cfg["Type"] == "columnboxes":
                self.make_columnbox(item[CONFIG_NAME], item[CONFIG_TITLE],
                    prefs[item[CONFIG_NAME]], item[CONFIG_COLUMN_TYPE], lo, i, k)
            # check for new row
            if cfg["Type"] == "checkboxes" and k < cfg["Columns"]:
                k += 1
            elif cfg["Type"] == "columnboxes" and k < cfg["Columns"] / 2:
                k += 2
            else:
                k = 0
                i += 1

    def make_exclusive(self, name, list):
        name = QButtonGroup(self)
        for item in list:
            name.addButton(item)

    def make_groupbox(self, name, title, parent):
        groupbox = QGroupBox(title, self)
        setattr(self, name, groupbox)
        parent.addWidget(groupbox)
        groupbox_layout = QGridLayout()
        setattr(self, name + "_layout", groupbox_layout)
        groupbox.setLayout(groupbox_layout)
        return groupbox_layout

    def make_checkbox(self, name, title, pref, parent, grid_row, grid_column):
        checkbox = QCheckBox(title, self)
        setattr(self, name, checkbox)
        checkbox.setChecked(pref)
        parent.addWidget(checkbox, grid_row, grid_column)

    def make_columnbox(self, name, label_text, pref, column_type, parent, grid_row, grid_column):
        # label
        column_label = QLabel(label_text, self)
        setattr(self, name + "label", column_label)

        # columnbox
        available_columns = self.get_custom_columns(column_type)
        column_box = self.CustomColumnComboBox(self, available_columns, pref)
        setattr(self, name, column_box)

        # put together and add
        column_label.setBuddy(column_box)
        parent.addWidget(column_label, grid_row, grid_column)
        parent.addWidget(column_box, grid_row, grid_column + 1)

    def get_custom_columns(self, column_type):
        '''
        Gets matching custom columns for column_type
        '''
        custom_columns = self.ia.gui.library_view.model().custom_columns
        available_columns = {}
        for key, column in custom_columns.iteritems():
            if column["is_multiple"]:
                is_multiple = True
            else:
                is_multiple = False
            if (column["datatype"] == column_type["datatype"] and
                    is_multiple == column_type["is_multiple"] and
                    column['display'].get('is_names', False) == column_type['is_names']):
                available_columns[key] = column
        return available_columns

    # modified from CountPages
    class CustomColumnComboBox(QComboBox):

        def __init__(self, parent, custom_columns={}, selected_column=''):
            QComboBox.__init__(self, parent)
            self.populate_combo(custom_columns, selected_column)

        def populate_combo(self, custom_columns, selected_column):
            self.clear()
            self.column_names = []
            selected_idx = 0
            custom_columns[""] = {"name": ""}
            for key in sorted(custom_columns.keys()):
                self.column_names.append(key)
                self.addItem('%s' % (custom_columns[key]['name']))
                if key == selected_column:
                    selected_idx = len(self.column_names) - 1
            self.setCurrentIndex(selected_idx)

        def select_column(self, key):
            selected_idx = 0
            for i, val in enumerate(self.column_names):
                if val == key:
                    selected_idx = i
                    break
            self.setCurrentIndex(selected_idx)

        def get_selected_column(self):
            return self.column_names[self.currentIndex()]
