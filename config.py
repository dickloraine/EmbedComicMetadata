#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
	from PyQt5.Qt import QWidget, QCheckBox, QGridLayout, QVBoxLayout, QGroupBox, QComboBox, QLabel
except ImportError:
	from PyQt4.Qt import QWidget, QCheckBox, QGridLayout, QVBoxLayout, QGroupBox, QComboBox, QLabel

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/EmbedComicMetadata')

# Set default custom columns
prefs.defaults['penciller_column'] = None
prefs.defaults['inker_column'] = None
prefs.defaults['colorist_column'] = None
prefs.defaults['letterer_column'] = None
prefs.defaults['cover_artist_column'] = None
prefs.defaults['editor_column'] = None
prefs.defaults['storyarc_column'] = None
prefs.defaults['characters_column'] = None
prefs.defaults['teams_column'] = None
prefs.defaults['locations_column'] = None
prefs.defaults['volume_column'] = None
prefs.defaults['genre_column'] = None

# Set default Options
prefs.defaults['cbi_embed'] = True
prefs.defaults['cix_embed'] = True
prefs.defaults['convert_cbr'] = True
prefs.defaults['convert_reading'] = False
prefs.defaults['delete_cbr'] = False
prefs.defaults['extended_menu'] = False
prefs.defaults['swap_names'] = False


class ConfigWidget(QWidget):

	def __init__(self, ia):
		QWidget.__init__(self)
		self.ia = ia
		self.l = QVBoxLayout()
		self.setLayout(self.l)

		# ----------------------------------------------------------------------
		# Custom Columns

		# Artists
		lca = self.make_groupbox("artists_custom_columns_box", 'Artists Custom Columns:', self.l)
		self.make_columnbox("penciller_column", 'Penciller Column:', prefs['penciller_column'], ["text"], lca, 1, 0)
		self.make_columnbox("inker_column", 'Inker Column:', prefs['inker_column'], ["text"], lca, 1, 2)
		self.make_columnbox("colorist_column", 'Colorist Column:', prefs['colorist_column'], ["text"], lca, 2, 0)
		self.make_columnbox("letterer_column", 'Letterer Column:', prefs['letterer_column'], ["text"], lca, 2, 2)
		self.make_columnbox("cover_artist_column", 'Cover Artist Column:', prefs['cover_artist_column'], ["text"], lca, 3, 0)
		self.make_columnbox("editor_column", 'Editor Column:', prefs['editor_column'], ["text"], lca, 3, 2)

		# Others
		lco = self.make_groupbox("other_custom_columns_box", 'Other Custom Columns:', self.l)
		self.make_columnbox("storyarc_column", 'Story Arc Column:', prefs['storyarc_column'], ["text"], lco, 1, 0)
		self.make_columnbox("characters_column", 'Characters Column:', prefs['characters_column'], ["text"], lco, 1, 2)
		self.make_columnbox("teams_column", 'Teams Column:', prefs['teams_column'], ["text"], lco, 2, 0)
		self.make_columnbox("locations_column", 'Locations Column:', prefs['locations_column'], ["text"], lco, 2, 2)
		self.make_columnbox("volume_column", 'Volume Column:', prefs['volume_column'], ["text"], lco, 3, 0)
		self.make_columnbox("genre_column", 'Genre Column:', prefs['genre_column'], ["text"], lco, 3, 2)

		# ----------------------------------------------------------------------
		# Options
		lo = self.make_groupbox("cfg_box", 'Options:', self.l)
		self.make_checkbox("cbi_checkbox", 'Write metadata in zip comment', prefs['cbi_embed'], lo, 1, 0)
		self.make_checkbox("cix_checkbox", 'Write metadata in ComicInfo.xml', prefs['cix_embed'], lo, 1, 1)
		self.make_checkbox("convert_cbr_checkbox", 'Auto convert cbr to cbz', prefs['convert_cbr'], lo, 2, 0)
		self.make_checkbox("convert_reading_checkbox", 'Auto convert while importing to calibre', prefs['convert_reading'], lo, 2, 1)
		self.make_checkbox("delete_cbr_checkbox", 'Delete cbr after conversion', prefs['delete_cbr'], lo, 3, 0)
		self.make_checkbox("extended_menu_checkbox", 'Extended Menu (needs calibre restart)', prefs['extended_menu'], lo, 3, 1)
		self.make_checkbox("swap_names_checkbox", 'Swap names to "LN, FN" when importing metadata', prefs['swap_names'], lo, 4, 0)

	def save_settings(self):
		# Save custom columns
		prefs['penciller_column'] = self.penciller_column.get_selected_column()
		prefs['inker_column'] = self.inker_column.get_selected_column()
		prefs['colorist_column'] = self.colorist_column.get_selected_column()
		prefs['letterer_column'] = self.letterer_column.get_selected_column()
		prefs['cover_artist_column'] = self.cover_artist_column.get_selected_column()
		prefs['editor_column'] = self.editor_column.get_selected_column()
		prefs['storyarc_column'] = self.storyarc_column.get_selected_column()
		prefs['characters_column'] = self.characters_column.get_selected_column()
		prefs['teams_column'] = self.teams_column.get_selected_column()
		prefs['locations_column'] = self.locations_column.get_selected_column()
		prefs['volume_column'] = self.volume_column.get_selected_column()
		prefs['genre_column'] = self.genre_column.get_selected_column()

		# Save Options
		prefs['cbi_embed'] = self.cbi_checkbox.isChecked()
		prefs['cix_embed'] = self.cix_checkbox.isChecked()
		prefs['convert_cbr'] = self.convert_cbr_checkbox.isChecked()
		prefs['convert_reading'] = self.convert_reading_checkbox.isChecked()
		prefs['delete_cbr'] = self.delete_cbr_checkbox.isChecked()
		prefs['extended_menu'] = self.extended_menu_checkbox.isChecked()
		prefs['swap_names'] = self.swap_names_checkbox.isChecked()

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

	def make_columnbox(self, name, label_text, pref, column_types, parent, grid_row, grid_column):
		# label
		column_label = QLabel(label_text, self)
		setattr(self, name + "label", column_label)

		# columnbox
		available_columns = self.get_custom_columns(column_types)
		column_box = self.CustomColumnComboBox(self, available_columns, pref)
		setattr(self, name, column_box)

		# put together and add
		column_label.setBuddy(column_box)
		parent.addWidget(column_label, grid_row, grid_column)
		parent.addWidget(column_box, grid_row, grid_column + 1)

	def get_custom_columns(self, column_types=[]):
		'''
		Gets matching custom columns for the types in the list column_types
		'''
		custom_columns = self.ia.gui.library_view.model().custom_columns
		available_columns = {}
		for key, column in custom_columns.iteritems():
			typ = column['datatype']
			if typ in column_types:
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
