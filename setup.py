#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'


# Define some column types
PERSON_TYPE = {"is_multiple": True, "is_names": True, "datatype": "text"}
TAG_TYPE    = {"is_multiple": True, "is_names": False, "datatype": "text"}
SINGLE_TYPE = {"is_multiple": False, "is_names": False, "datatype": "text"}
FLOAT_TYPE  = {"is_multiple": False, "is_names": False, "datatype": "float"}
SERIES_TYPE = {"is_multiple": False, "is_names": False, "datatype": "series"}

# Some constants for ease of reading
CONFIG_NAME = 0
CONFIG_TITLE = 1
CONFIG_DEFAULT = 2
CONFIG_COLUMN_TYPE = 3
CONFIG_DESCRIPTION = 1
CONFIG_TRIGGER_FUNC = 2
CONFIG_TRIGGER_ARG = 3


def get_configuration():
    '''
    All configuration for preferences and the UI-Menu is made with the
    informations given here. No need to change anything in config.py or ui.py,
    if new preferences or menu items need to be made.

    Name: The internal name for the preference group
    Title: The Label in the config menu
    Type: Either "columnboxes" or "checkboxes"
    Columns: How many columns the group should have in the config menu
    Items: The preferences in the menu group. Has the form:
           [preference_name, displayed name, default_state, if column: columntype]
    UI_Action_Items: The buttons in the toolbar menu. Has the form:
           [name, displayed_text, triggerfunc, triggerfunc_arg]
    '''
    from calibre_plugins.EmbedComicMetadata.main import embed_into_comic, import_to_calibre, embed_cover, convert

    # configuration
    config = [
        {
            "Name": "artists_custom_columns",
            "Title": "Artists Custom Columns:",
            "Type": "columnboxes",
            "Columns": 2,
            "Items": [
                ["penciller_column", 'Penciller Column:', None, PERSON_TYPE],
                ["inker_column", 'Inker Column:', None, PERSON_TYPE],
                ["colorist_column", 'Colorist Column:', None, PERSON_TYPE],
                ["letterer_column", 'Letterer Column:', None, PERSON_TYPE],
                ["cover_artist_column", 'Cover Artist Column:', None, PERSON_TYPE],
                ["editor_column", 'Editor Column:', None, PERSON_TYPE]
            ]
        },
        {
            "Name": "other_custom_columns",
            "Title": "Other Custom Columns:",
            "Type": "columnboxes",
            "Columns": 2,
            "Items": [
                ["storyarc_column", 'Story Arc Column:', None, SINGLE_TYPE],
                ["characters_column", 'Characters Column:', None, TAG_TYPE],
                ["teams_column", 'Teams Column:', None, TAG_TYPE],
                ["locations_column", 'Locations Column:', None, TAG_TYPE],
                ["volume_column", 'Volume Column:', None, SINGLE_TYPE],
                ["genre_column", 'Genre Column:', None, TAG_TYPE]
            ]
        },
        {
            "Name": "options",
            "Title": "Options:",
            "Type": "checkboxes",
            "Columns": 2,
            "Items": [
                ["cbi_embed", 'Write metadata in zip comment', True],
                ["cix_embed", 'Write metadata in ComicInfo.xml', True],
                ["read_cbi", 'Import metadata from zip comment', True],
                ["read_cix", 'Import metadata from ComicInfo.xml', True],
                ["convert_cbr", 'Auto convert cbr to cbz', True],
                ["convert_reading", 'Auto convert while importing to calibre', True],
                ["delete_cbr", 'Delete cbr after conversion', True],
                ["swap_names", 'Swap names to "LN, FN" when importing metadata', True]
            ]
        },
        {
            "Name": "main_button",
            "Title": "Main Button Action (needs a calibre restart):",
            "Type": "checkboxes",
            "Columns": 2,
            "Items": [
                ["main_embed", 'Embed metadata', True],
                ["main_import", 'Import metadata', True],
            ]
        },
        {
            "Name": "menu",
            "Title": "Menu Buttons:",
            "Type": "checkboxes",
            "Columns": 3,
            "Items": [
                ["embed", 'Show embed both button', True],
                ["embedcbi", 'Show embed cbi button', True],
                ["embedcix", 'Show embed cix button', True],
                ["read_both", 'Show import both button', True],
                ["import_cix", 'Show import cix button', True],
                ["import_cbi", 'Show import cbi button', True],
                ["convert", 'Show convert button', True],
                ["cover", 'Show embed cover button', True]
            ],
            "UI_Action_Items": [
                ["read_both", 'Import Metadata from the comic archive into calibre', import_to_calibre, "both"],
                ["import_cix", "Import Comic Rack Metadata from the comic archive into calibre", import_to_calibre, "cix"],
                ["import_cbi", "Import Comment Metadata from the comic archive into calibre", import_to_calibre, "cbi"],
                ["seperator"],
                ["embed", "Embed both Comic Metadata types", embed_into_comic, "both"],
                ["embedcbi", "Only embed Metadata in zip comment", embed_into_comic, "cbi"],
                ["embedcix", "Only embed Metadata in ComicInfo.xml", embed_into_comic, "cix"],
                ["convert", "Only convert cbr to cbz", convert, None],
                ["cover", "Embed the calibre cover", embed_cover, None],
                ["seperator"]
            ]
        }
    ]

    return config


def map_over_config_items(func, group_name, items_name="Items"):
    config = get_configuration()

    for group in config:
        if group["Name"] == group_name:
            for item in group[items_name]:
                func(item)
