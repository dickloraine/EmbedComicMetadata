#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import QMenu
except ImportError:
    from PyQt4.Qt import QMenu

from functools import partial

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.setup import CONFIG_NAME, CONFIG_DESCRIPTION, CONFIG_TRIGGER_FUNC, CONFIG_TRIGGER_ARG, map_over_config_items


class EmbedComicMetadata(InterfaceAction):

    name = 'Embed Comic Metadata'

    # Declare the main action associated with this plugin
    if prefs["main_import"]:
        action_spec = ('Import Comic Metadata', None,
                'Imports the metadata from the comic to calibre', None)
    else:
        action_spec = ('Embed Comic Metadata', None,
                'Embeds calibres metadata into the comic', None)

    def genesis(self):
        # menu
        self.menu = QMenu(self.gui)

        # Set the icon for this interface action
        icon = get_icons('images/icon.png')  # need to import this?

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.main_menu_triggered)

        # build menu
        self.menu.clear()
        map_over_config_items(self.build_menu, "menu", "UI_Action_Items")
        self.menu_action("configure", "Configure",
            partial(self.interface_action_base_plugin.do_user_config, (self.gui)))
        self.toggle_menu_items()

    def build_menu(self, item):
        if item[CONFIG_NAME] == "seperator":
            self.menu.addSeparator()
        else:
            if item[CONFIG_TRIGGER_ARG]:
                triggerfunc = partial(item[CONFIG_TRIGGER_FUNC], self, item[CONFIG_TRIGGER_ARG])
            else:
                triggerfunc = partial(item[CONFIG_TRIGGER_FUNC], self)
            self.menu_action(item[CONFIG_NAME], item[CONFIG_DESCRIPTION], triggerfunc)

    def toggle_menu_items(self):
        map_over_config_items(self._toggle_menu_items, "menu")

    def _toggle_menu_items(self, item):
        action = getattr(self, item[CONFIG_NAME])
        action.setVisible(prefs[item[CONFIG_NAME]])

    def main_menu_triggered(self):
        from calibre_plugins.EmbedComicMetadata.main import embed_into_comic, import_to_calibre

        # Check the preferences for what should be done
        if (prefs['read_cbi'] and prefs['read_cix']) or (prefs['cbi_embed'] and prefs['cix_embed']):
            action = "both"
        elif (prefs['read_cbi']) or (prefs['cbi_embed']):
            action = "cbi"
        elif (prefs['read_cix']) or (prefs['cix_embed']):
            action = "cix"
        else:
            return error_dialog(self.gui, 'Cannot update metadata',
                        'No embed format selected', show=True)

        if prefs["main_import"]:
            import_to_calibre(self, action)
        else:
            embed_into_comic(self, action)

    def apply_settings(self):
        from calibre_plugins.EmbedComicMetadata.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

    def menu_action(self, name, title, triggerfunc):
        action = self.create_menu_action(self.menu, name, title, icon=None,
            shortcut=None, description=None, triggered=triggerfunc,
            shortcut_name=None)
        setattr(self, name, action)
