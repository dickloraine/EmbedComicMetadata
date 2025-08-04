from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from functools import partial
from calibre.gui2 import error_dialog, info_dialog

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.languages.lang import _L
from calibre_plugins.EmbedComicMetadata.comicmetadata import ComicMetadata

import sys

python3 = sys.version_info[0] > 2

def import_to_calibre(ia, action):
    def _import_to_calibre(metadata):
        metadata.get_comic_metadata_from_file()
        if action == "both" and metadata.comic_metadata:
            metadata.import_comic_metadata_to_calibre(metadata.comic_metadata)
        elif action == "cix" and metadata.cix_metadata:
            metadata.import_comic_metadata_to_calibre(metadata.cix_metadata)
        elif action == "cbi" and metadata.cbi_metadata:
            metadata.import_comic_metadata_to_calibre(metadata.cbi_metadata)
        else:
            return False
        return True

    iterate_over_books(ia, _import_to_calibre,
                       _L["Updated Calibre Metadata"],
                       _L['Updated calibre metadata for {} book(s)'],
                       _L['The following books had no metadata: {}'],
                       prefs['convert_reading'])


def embed_into_comic(ia, action):
    def _embed_into_comic(metadata):
        if metadata.format != "cbz":
            return False
        metadata.overlay_metadata()
        if action == "both" or action == "cix":
            metadata.embed_cix_metadata()
        if action == "both" or action == "cbi":
            metadata.embed_cbi_metadata()
        metadata.add_updated_comic_to_calibre()
        return True

    iterate_over_books(ia, _embed_into_comic,
                       _L["Updated comics"],
                       _L['Updated the metadata in the files of {} comics'],
                       _L['The following books were not updated: {}'])


def convert(ia):
    iterate_over_books(ia, partial(convert_to_cbz, ia),
                       _L["Converted files"],
                       _L['Converted {} book(s) to cbz'],
                       _L['The following books were not converted: {}'],
                       False)


def embed_cover(ia):
    def _embed_cover(metadata):
        if metadata.format != "cbz":
            return False
        metadata.update_cover()
        metadata.add_updated_comic_to_calibre()
        return True

    iterate_over_books(ia, _embed_cover,
                       _L["Updated Covers"],
                       _L['Embeded {} covers'],
                       _L['The following covers were not embeded: {}'])


def count_pages(ia):
    def _count_pages(metadata):
        if metadata.format != "cbz":
            return False
        return metadata.action_count_pages()

    iterate_over_books(ia, _count_pages,
                       _L["Counted pages"],
                       _L['Counted pages in {} comics'],
                       _L['The following comics were not counted: {}'])


def remove_metadata(ia):
    def _remove_metadata(metadata):
        if metadata.format != "cbz":
            return False
        metadata.remove_embedded_metadata()
        metadata.add_updated_comic_to_calibre()
        return True

    iterate_over_books(ia, _remove_metadata,
                        _L["Removed metadata"],
                        _L['Removed metadata in {} comics'],
                        _L['The following comics did not have metadata removed: {}'])


def get_image_size(ia):
    def _get_image_size(metadata):
        if metadata.format != "cbz":
            return False
        return metadata.action_picture_size()

    iterate_over_books(ia, _get_image_size,
                       _L["Updated Calibre Metadata"],
                       _L['Updated calibre metadata for {} book(s)'],
                       _L['The following books were not updated: {}'])


def iterate_over_books(ia, func, title, ptext, notptext,
                       should_convert=None,
                       convtext=_L["The following comics were converted to cbz: {}"]):
    '''
    Iterates over all selected books. For each book, it checks if it should be
    converted to cbz and then applies func to the book.
    After all books are processed, gives a completion message.
    '''
    processed = []
    not_processed = []
    converted = []

    if should_convert is None:
        should_convert = prefs["convert_cbr"]

    # iterate through the books
    for book_id in get_selected_books(ia):
        metadata = ComicMetadata(book_id, ia)

        # sanity check
        if metadata.format is None:
            not_processed.append(metadata.info)
            continue

        if should_convert and convert_to_cbz(ia, metadata):
            converted.append(metadata.info)

        if func(metadata):
            processed.append(metadata.info)
        else:
            not_processed.append(metadata.info)

    # show a completion message
    msg = ptext.format(len(processed))
    if should_convert and len(converted) > 0:
        msg += '\n' + convtext.format(lst2string(converted))
    if len(not_processed) > 0:
        msg += '\n' + notptext.format(lst2string(not_processed))
    info_dialog(ia.gui, title, msg, show=True)


def get_selected_books(ia):
    # Get currently selected books
    rows = ia.gui.library_view.selectionModel().selectedRows()
    if not rows or len(rows) == 0:
        return error_dialog(ia.gui, _L['Cannot update metadata'],
                            _L['No books selected'], show=True)
    # Map the rows to book ids
    return map(ia.gui.library_view.model().id, rows)


def lst2string(lst):
    if python3:
        return "\n    " + "\n    ".join(lst)
    return "\n    " + "\n    ".join(item.encode('utf-8') for item in lst)


def convert_to_cbz(ia, metadata):
    if metadata.format == "cbr" or (metadata.format == "rar" and prefs['convert_archives']):
        metadata.convert_cbr_to_cbz()
        if prefs['delete_cbr']:
            ia.gui.current_db.new_api.remove_formats({metadata.book_id: {"cbr", "rar"}})
        return True
    elif metadata.format == "zip" and prefs['convert_archives']:
        metadata.convert_zip_to_cbz()
        if prefs['delete_cbr']:
            ia.gui.current_db.new_api.remove_formats({metadata.book_id: {"zip"}})
        return True
    return False
