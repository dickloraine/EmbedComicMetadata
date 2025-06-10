#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import QMenu, QIcon, QPixmap
except ImportError:
    from PyQt4.Qt import QMenu, QIcon, QPixmap

from functools import partial

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.languages.lang import _L
from calibre_plugins.EmbedComicMetadata.ini import (
    get_configuration, CONFIG_NAME, CONFIG_DESCRIPTION, CONFIG_TRIGGER_FUNC,
    CONFIG_TRIGGER_ARG, CONFIG_MENU)


config = get_configuration()


class EmbedComicMetadata(InterfaceAction):

    name = 'Embed Comic Metadata'

    # Declare the main action associated with this plugin
    if prefs["main_import"]:
        action_spec = (_L['Import Comic Metadata'], None,
                       _L['Imports the metadata from the comic to calibre'], None)
    else:
        action_spec = (_L['Embed Comic Metadata'], None,
                       _L['Embeds calibres metadata into the comic'], None)

    def genesis(self):
        # menu
        self.menu = QMenu(self.gui)

        # Get the icon for this interface action
        icon = self.get_icon('images/embed_comic_metadata.png')

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.main_menu_triggered)

        # build menu
        self.menu.clear()
        self.build_menu()
        self.toggle_menu_items()

    def build_menu(self):
        from calibre_plugins.EmbedComicMetadata.ini import get_ui_action_items_config
        menu_config = get_ui_action_items_config()
        for item in menu_config["UI_Action_Items"]:
            if item[CONFIG_NAME] == "seperator":
                self.menu.addSeparator()
                continue
            elif item[CONFIG_TRIGGER_ARG]:
                triggerfunc = partial(item[CONFIG_TRIGGER_FUNC], self, item[CONFIG_TRIGGER_ARG])
            else:
                triggerfunc = partial(item[CONFIG_TRIGGER_FUNC], self)
            self.menu_action(item[CONFIG_NAME], item[CONFIG_DESCRIPTION], triggerfunc)
        # add configuration entry
        self.menu_action("configure", _L["Configure"],
                         partial(self.interface_action_base_plugin.do_user_config, (self.gui)))

    def toggle_menu_items(self):
        for item in config[CONFIG_MENU]["Items"]:
            action = getattr(self, item[CONFIG_NAME])
            action.setVisible(prefs[item[CONFIG_NAME]])

    def main_menu_triggered(self):
        from calibre_plugins.EmbedComicMetadata.main import embed_into_comic, import_to_calibre

        i = prefs["main_import"]
        # Check the preferences for what should be done
        if (i and prefs['read_cbi'] and prefs['read_cix']) or (
                not i and prefs['cbi_embed'] and prefs['cix_embed']):
            action = "both"
        elif (i and prefs['read_cbi']) or (not i and prefs['cbi_embed']):
            action = "cbi"
        elif (i and prefs['read_cix']) or (not i and prefs['cix_embed']):
            action = "cix"
        else:
            return error_dialog(self.gui, _L['Cannot update metadata'],
                                _L['No embed format selected'], show=True)

        if i:
            import_to_calibre(self, action)
        else:
            embed_into_comic(self, action)

    def apply_settings(self):
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

    def menu_action(self, name, title, triggerfunc):
        action = self.create_menu_action(self.menu, name, title, icon=None,
                                         shortcut=None, description=None,
                                         triggered=triggerfunc, shortcut_name=None)
        setattr(self, name, action)

    def get_icon(self, icon_name):
        import os
        from calibre.utils.config import config_dir

        # Check to see whether the icon exists as a Calibre resource
        # This will enable skinning if the user stores icons within a folder like:
        # ...\AppData\Roaming\calibre\resources\images\Plugin Name\
        icon_path = os.path.join(config_dir, 'resources', 'images', self.name,
                                 icon_name.replace('images/', ''))
        if os.path.exists(icon_path):
            pixmap = QPixmap()
            pixmap.load(icon_path)
            return QIcon(pixmap)
        # As we did not find an icon elsewhere, look within our zip resources
        return get_icons(icon_name)
