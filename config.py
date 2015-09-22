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

# Set default Options
prefs.defaults['cbi_embed'] = True
prefs.defaults['cix_embed'] = True
prefs.defaults['convert_cbr'] = True
prefs.defaults['convert_reading'] = False
prefs.defaults['delete_cbr'] = False
prefs.defaults['extended_menu'] = False


class ConfigWidget(QWidget):

	def __init__(self, ia):
		QWidget.__init__(self)
		self.ia = ia
		self.l = QVBoxLayout()
		self.setLayout(self.l)

		# ----------------------------------------------------------------------
		# Custom Columns
		self.custom_columns_box = QGroupBox('Custom Columns:')
		self.l.addWidget(self.custom_columns_box)
		self.custom_columns_layout = QGridLayout()
		self.custom_columns_box.setLayout(self.custom_columns_layout)

		# Artists
		self.make_columnbox("penciller_column", 'Penciller Column:', prefs['penciller_column'], ["text"], 1, 0)
		self.make_columnbox("inker_column", 'Inker Column:', prefs['inker_column'], ["text"], 1, 2)
		self.make_columnbox("colorist_column", 'Colorist Column:', prefs['colorist_column'], ["text"], 2, 0)
		self.make_columnbox("letterer_column", 'Letterer Column:', prefs['letterer_column'], ["text"], 2, 2)
		self.make_columnbox("cover_artist_column", 'Cover Artist Column:', prefs['cover_artist_column'], ["text"], 3, 0)
		self.make_columnbox("editor_column", 'Editor Column:', prefs['editor_column'], ["text"], 3, 2)

		# ----------------------------------------------------------------------
		# Options
		self.cfg_box = QGroupBox('Options:')
		self.l.addWidget(self.cfg_box)
		self.cfg_layout = QGridLayout()
		self.cfg_box.setLayout(self.cfg_layout)

		self.make_checkbox("cbi_checkbox", 'Write metadata in zip comment', prefs['cbi_embed'], 1, 0)
		self.make_checkbox("cix_checkbox", 'Write metadata in ComicInfo.xml', prefs['cix_embed'], 1, 1)
		self.make_checkbox("convert_cbr_checkbox", 'Auto convert cbr to cbz', prefs['convert_cbr'], 2, 0)
		self.make_checkbox("convert_reading_checkbox", 'Auto convert while importing to calibre', prefs['convert_reading'], 2, 1)
		self.make_checkbox("delete_cbr_checkbox", 'Delete cbr after conversion', prefs['delete_cbr'], 3, 0)
		self.make_checkbox("extended_menu_checkbox", 'Extended Menu (needs calibre restart)', prefs['extended_menu'], 3, 1)

	def save_settings(self):
		# Save custom columns
		prefs['penciller_column'] = self.penciller_column.get_selected_column()
		prefs['inker_column'] = self.inker_column.get_selected_column()
		prefs['colorist_column'] = self.colorist_column.get_selected_column()
		prefs['letterer_column'] = self.letterer_column.get_selected_column()
		prefs['cover_artist_column'] = self.cover_artist_column.get_selected_column()
		prefs['editor_column'] = self.editor_column.get_selected_column()

		# Save default Options
		prefs['cbi_embed'] = self.cbi_checkbox.isChecked()
		prefs['cix_embed'] = self.cix_checkbox.isChecked()
		prefs['convert_cbr'] = self.convert_cbr_checkbox.isChecked()
		prefs['convert_reading'] = self.convert_reading_checkbox.isChecked()
		prefs['delete_cbr'] = self.delete_cbr_checkbox.isChecked()
		prefs['extended_menu'] = self.extended_menu_checkbox.isChecked()

	def make_checkbox(self, name, title, pref, grid_row, grid_column):
		setattr(self, name, QCheckBox(title, self))
		checkbox = getattr(self, name)
		checkbox.setChecked(pref)
		self.cfg_layout.addWidget(checkbox, grid_row, grid_column)

	def make_columnbox(self, name, label_text, pref, column_types, grid_row, grid_column):
		# label
		setattr(self, name + "label", QLabel(label_text))
		column_label = getattr(self, name + "label")

		# columnbox
		available_columns = self.get_custom_columns(column_types)
		setattr(self, name, self.CustomColumnComboBox(self, available_columns, pref))
		column_box = getattr(self, name)

		# put together and add
		column_label.setBuddy(column_box)
		self.custom_columns_layout.addWidget(column_label, grid_row, grid_column)
		self.custom_columns_layout.addWidget(column_box, grid_row, grid_column + 1)

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
