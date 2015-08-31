#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import QToolButton, QMenu
except ImportError:
    from PyQt4.Qt import QToolButton, QMenu
# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog

from calibre_plugins.EmbedComicMetadata.calibrecomic import update_metadata
from calibre_plugins.EmbedComicMetadata.config import prefs

class EmbedComicMetadata(InterfaceAction):

    name = 'Embed Comic Metadata'

    # Declare the main action associated with this plugin
    action_spec = ('Embed Comic Metadata', None,
            'Run the Embed Comic Metadata Plugin', None)

    def genesis(self):
        # This method is called once per plugin, do initial setup here
		self.menu = QMenu(self.gui)
		self.build_menu()
				
        # Set the icon for this interface action
        icon = get_icons('images/icon.png')

        # The qaction is automatically created from the action_spec defined
        # above
		self.qaction.setMenu(self.menu)
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.menu_triggered)

	def build_menu(self):
		m = self.menu
        m.clear()
		self.create_menu_action(m, "embed", "Embed both Comic Metadata types", icon=None, shortcut=None,
							description=None, triggered=self.both_triggered, shortcut_name=None)
		self.create_menu_action(m, "embedcbi", "Only embed Metadata in comment", icon=None, shortcut=None,
							description=None, triggered=self.cbi_triggered, shortcut_name=None)
		self.create_menu_action(m, "embedcix", "Only embed Metadata in ComicInfo.xml", icon=None, shortcut=None,
							description=None, triggered=self.cix_triggered, shortcut_name=None)
		self.create_menu_action(m, "convert", "Only convert cbr to cbz", icon=None, shortcut=None,
							description=None, triggered=self.convert_triggered, shortcut_name=None)
		m.addSeparator()
		self.create_menu_action(m, "configure", "Configure", icon=None, shortcut=None,
							description=None, triggered=self.configure_triggered, shortcut_name=None)
		
    def menu_triggered(self):
		# Check the preferences for what should be embedded
		if prefs['cbi_embed'] and prefs['cix_embed']:
			do_embed = "both"
		elif prefs['cbi_embed']:
			do_embed = "cbi"
		elif prefs['cix_embed']:
			do_embed = "cix"
		else:
			return error_dialog(self.gui, 'Cannot update metadata',
						 'No embed format selected', show=True)
		# embed the metadata
        update_metadata(self, do_embed)
		
	def both_triggered(self):
		update_metadata(self, "both")
	
	def cbi_triggered(self):
		update_metadata(self, "cbi")
		
	def cix_triggered(self):
		update_metadata(self, "cix")
	
	def convert_triggered(self):
		update_metadata(self, "just_convert")
	
	def configure_triggered(self):
		self.interface_action_base_plugin.do_user_config(self.gui)

    def apply_settings(self):
        from calibre_plugins.EmbedComicMetadata.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs