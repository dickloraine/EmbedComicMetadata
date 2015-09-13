#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
	from PyQt5.Qt import QWidget, QHBoxLayout, QCheckBox
except ImportError:
	from PyQt4.Qt import QWidget, QHBoxLayout, QCheckBox

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
prefs.defaults['delete_cbr'] = False


class ConfigWidget(QWidget):

	def __init__(self):
		QWidget.__init__(self)
		self.l = QHBoxLayout()
		self.setLayout(self.l)

		self.cbi_checkbox = QCheckBox('Write metadata in zip comment', self)
		self.cbi_checkbox.setChecked(prefs['cbi_embed'])
		self.l.addWidget(self.cbi_checkbox)

		self.cix_checkbox = QCheckBox('Write metadata in ComicInfo.xml', self)
		self.cix_checkbox.setChecked(prefs['cix_embed'])
		self.l.addWidget(self.cix_checkbox)

		self.convert_cbr_checkbox = QCheckBox('Auto convert cbr to cbz', self)
		self.convert_cbr_checkbox.setChecked(prefs['convert_cbr'])
		self.l.addWidget(self.convert_cbr_checkbox)

		self.delete_cbr_checkbox = QCheckBox('Delete cbr after conversion', self)
		self.delete_cbr_checkbox.setChecked(prefs['delete_cbr'])
		self.l.addWidget(self.delete_cbr_checkbox)

	def save_settings(self):
		prefs['cbi_embed'] = self.cbi_checkbox.isChecked()
		prefs['cix_embed'] = self.cix_checkbox.isChecked()
		prefs['convert_cbr'] = self.convert_cbr_checkbox.isChecked()
		prefs['delete_cbr'] = self.delete_cbr_checkbox.isChecked()
