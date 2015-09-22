#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
	from PyQt5.Qt import QWidget, QCheckBox, QGridLayout, QVBoxLayout, QGroupBox
except ImportError:
	from PyQt4.Qt import QWidget, QCheckBox, QGridLayout, QVBoxLayout, QGroupBox

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/EmbedComicMetadata')

# Set defaults
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
		self.custom_cloumns_box = QGroupBox('Custom Columns:')
		self.l.addWidget(self.custom_cloumns_box)
		self.custom_cloumns_layout = QGridLayout()
		self.custom_cloumns_box.setLayout(self.custom_cloumns_layout)

		# ----------------------------------------------------------------------
		# Options
		self.cfg_box = QGroupBox('Options:')
		self.l.addWidget(self.cfg_box)
		self.cfg_layout = QGridLayout()
		self.cfg_box.setLayout(self.cfg_layout)

		self.make_checkbox(self.cfg_layout, "cbi_checkbox", 'Write metadata in zip comment', prefs['cbi_embed'], 1, 0)
		self.make_checkbox(self.cfg_layout, "cix_checkbox", 'Write metadata in ComicInfo.xml', prefs['cix_embed'], 1, 1)
		self.make_checkbox(self.cfg_layout, "convert_cbr_checkbox", 'Auto convert cbr to cbz', prefs['convert_cbr'], 2, 0)
		self.make_checkbox(self.cfg_layout, "convert_reading_checkbox", 'Auto convert while importing to calibre', prefs['convert_reading'], 2, 1)
		self.make_checkbox(self.cfg_layout, "delete_cbr_checkbox", 'Delete cbr after conversion', prefs['delete_cbr'], 3, 0)
		self.make_checkbox(self.cfg_layout, "extended_menu_checkbox", 'Extended Menu (needs calibre restart)', prefs['extended_menu'], 3, 1)

	def save_settings(self):
		prefs['cbi_embed'] = self.cbi_checkbox.isChecked()
		prefs['cix_embed'] = self.cix_checkbox.isChecked()
		prefs['convert_cbr'] = self.convert_cbr_checkbox.isChecked()
		prefs['convert_reading'] = self.convert_reading_checkbox.isChecked()
		prefs['delete_cbr'] = self.delete_cbr_checkbox.isChecked()
		prefs['extended_menu'] = self.extended_menu_checkbox.isChecked()

	def make_checkbox(self, parent, name, title, pref, grid_row, grid_column):
		setattr(self, name, QCheckBox(title, self))
		checkbox = getattr(self, name)
		checkbox.setChecked(pref)
		parent.addWidget(checkbox, grid_row, grid_column)

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
