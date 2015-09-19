#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
	from PyQt5.Qt import QWidget, QCheckBox, QGridLayout
except ImportError:
	from PyQt4.Qt import QWidget, QCheckBox, QGridLayout

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

	def __init__(self):
		QWidget.__init__(self)
		self.l = QGridLayout()
		self.l.setSpacing(10)
		self.setLayout(self.l)

		self.cbi_checkbox = QCheckBox('Write metadata in zip comment', self)
		self.cbi_checkbox.setChecked(prefs['cbi_embed'])
		self.l.addWidget(self.cbi_checkbox, 1, 0)

		self.cix_checkbox = QCheckBox('Write metadata in ComicInfo.xml', self)
		self.cix_checkbox.setChecked(prefs['cix_embed'])
		self.l.addWidget(self.cix_checkbox, 1, 1)

		self.convert_cbr_checkbox = QCheckBox('Auto convert cbr to cbz', self)
		self.convert_cbr_checkbox.setChecked(prefs['convert_cbr'])
		self.l.addWidget(self.convert_cbr_checkbox, 2, 0)

		self.convert_reading_checkbox = QCheckBox('Auto convert while importing to calibre', self)
		self.convert_reading_checkbox.setChecked(prefs['convert_reading'])
		self.l.addWidget(self.convert_reading_checkbox, 2, 1)

		self.delete_cbr_checkbox = QCheckBox('Delete cbr after conversion', self)
		self.delete_cbr_checkbox.setChecked(prefs['delete_cbr'])
		self.l.addWidget(self.delete_cbr_checkbox, 2, 2)

		self.extended_menu_checkbox = QCheckBox('Extended Menu (needs calibre restart)', self)
		self.extended_menu_checkbox.setChecked(prefs['extended_menu'])
		self.l.addWidget(self.extended_menu_checkbox, 3, 0)

	def save_settings(self):
		prefs['cbi_embed'] = self.cbi_checkbox.isChecked()
		prefs['cix_embed'] = self.cix_checkbox.isChecked()
		prefs['convert_cbr'] = self.convert_cbr_checkbox.isChecked()
		prefs['convert_reading'] = self.convert_reading_checkbox.isChecked()
		prefs['delete_cbr'] = self.delete_cbr_checkbox.isChecked()
		prefs['extended_menu'] = self.extended_menu_checkbox.isChecked()
