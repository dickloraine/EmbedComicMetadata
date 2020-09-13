from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import (QWidget, QCheckBox, QGridLayout, QVBoxLayout,
                          QGroupBox, QComboBox, QLabel, QButtonGroup, QScrollArea)
except ImportError:
    from PyQt4.Qt import (QWidget, QCheckBox, QGridLayout, QScrollArea,
                          QVBoxLayout, QGroupBox, QComboBox, QLabel, QButtonGroup)

from functools import partial

from calibre.utils.config import JSONConfig
from calibre_plugins.EmbedComicMetadata.ini import (
    get_configuration, CONFIG_NAME, CONFIG_TITLE, CONFIG_DEFAULT, CONFIG_COLUMN_TYPE)

import sys

python3 = sys.version_info[0] > 2

# python 2/3 compatibility
def iteritems(d):
    if python3:
        return iter(d.items())
    return iter(d.iteritems())


# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/EmbedComicMetadata')

config = get_configuration()

# set defaults
prefs.defaults = {item[CONFIG_NAME]: item[CONFIG_DEFAULT]
                  for group in config for item in group["Items"]}


class ConfigWidget(QWidget):

    def __init__(self, ia):
        QWidget.__init__(self)
        self.ia = ia
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # make the config menu as a widget
        self.config_menu = self.make_menu()

        # make a scroll area to hold the menu and add it to the layout
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.config_menu)
        self.layout.addWidget(self.scroll)

    def save_settings(self):
        for group in config:
            if group["Type"] == "columnboxes":
                func = self.CustomColumnComboBox.get_selected_column
            else:
                func = QCheckBox.isChecked
            for item in group["Items"]:
                name = getattr(self, item[CONFIG_NAME])
                prefs[item[CONFIG_NAME]] = func(name)
        # rebuild the menu
        self.ia.toggle_menu_items()

    def make_menu(self):
        config_menu = QWidget()
        self.l = QVBoxLayout()
        config_menu.setLayout(self.l)

        # add the menu items
        for group in config:
            self.make_submenu(group, self.l)

        return config_menu

    def make_submenu(self, group, parent):
        lo = self.make_groupbox(group, parent)

        # get the right builder function for the group type
        if group["Type"] == "checkboxes":
            func = partial(self.make_checkbox, lo, group["Columns"])
        else:
            func = partial(self.make_columnbox, lo, group["Columns"])

        # loop through the items and build the entries
        grid_row, grid_column = 1, 0
        for item in group["Items"]:
            grid_row, grid_column = func(item, grid_row, grid_column)

        # make buttons exclusive
        if "Exclusive_Items" in group:
            for item_list in group["Exclusive_Items"]:
                self.make_exclusive(item_list)

    def make_exclusive(self, item_list):
        excl_group = QButtonGroup(self)
        for item in item_list:
            item = getattr(self, item)
            excl_group.addButton(item)

    def make_groupbox(self, group, parent):
        groupbox = QGroupBox(group["Title"], self)
        setattr(self, group["Name"] + "_box", groupbox)
        parent.addWidget(groupbox)
        groupbox_layout = QGridLayout()
        setattr(self, group["Name"] + "_layout", groupbox_layout)
        groupbox.setLayout(groupbox_layout)
        return groupbox_layout

    def make_checkbox(self, parent, columns, item, grid_row, grid_column):
        checkbox = QCheckBox(item[CONFIG_TITLE], self)
        setattr(self, item[CONFIG_NAME], checkbox)
        checkbox.setChecked(prefs[item[CONFIG_NAME]])
        parent.addWidget(checkbox, grid_row, grid_column)

        # check for new row
        if grid_column < columns - 1:
            return grid_row, grid_column + 1
        return grid_row + 1, 0

    def make_columnbox(self, parent, columns, item, grid_row, grid_column):
        # label
        column_label = QLabel(item[CONFIG_TITLE], self)
        setattr(self, item[CONFIG_NAME] + "label", column_label)

        # columnbox
        available_columns = self.get_custom_columns(item[CONFIG_COLUMN_TYPE])
        column_box = self.CustomColumnComboBox(self, available_columns, prefs[item[CONFIG_NAME]])
        setattr(self, item[CONFIG_NAME], column_box)

        # put together and add
        column_label.setBuddy(column_box)
        parent.addWidget(column_label, grid_row, grid_column)
        parent.addWidget(column_box, grid_row, grid_column + 1)

        # check for new row
        if grid_column < columns / 2:
            return grid_row, grid_column + 2
        return grid_row + 1, 0

    def get_custom_columns(self, column_type):
        '''
        Gets matching custom columns for column_type
        '''
        custom_columns = self.ia.gui.library_view.model().custom_columns
        available_columns = {}
        for key, column in iteritems(custom_columns):
            if (column["datatype"] in column_type["datatype"] and
                    bool(column["is_multiple"]) == column_type["is_multiple"] and
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
