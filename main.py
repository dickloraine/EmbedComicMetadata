from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from calibre.gui2 import error_dialog, info_dialog

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.languages.lang import _L
from calibre_plugins.EmbedComicMetadata.comicmetadata import ComicMetadata


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
        True, "convert_reading")


def embed_into_comic(ia, action):
    def _embed_into_comic(metadata):
        if metadata.format == "cbr":
            return False
        metadata.get_comic_metadata_from_file()
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
    def _convert(metadata):
        if metadata.format != "cbr":
            return False
        metadata.convert_to_cbz()
        if prefs['delete_cbr']:
            ia.gui.current_db.new_api.remove_formats({metadata.book_id: {'cbr'}})
        return True

    iterate_over_books(ia, _convert,
        _L["Converted files"],
        _L['Converted {} book(s) to cbz'],
        _L['The following books were not converted: {}'],
        False)


def embed_cover(ia):
    def _embed_cover(metadata):
        if metadata.format == "cbr":
            return False
        metadata.update_cover()
        metadata.add_updated_comic_to_calibre()
        return True

    iterate_over_books(ia, _embed_cover,
        _L["Updated Covers"],
        _L['Embeded {} covers'],
        _L['The following covers were not embeded: {}'])


def iterate_over_books(ia, func, title, ptext, notptext,
        convert=True, convaction="convert_cbr",
        convtext=_L["The following comics were converted to cbz: {}"]):
    '''
    Iterates over all selected books. For each book, it checks if it should be
    converted to cbz and then applies func to the book.
    After all books are processed, gives a completion message.
    '''

    processed = []
    not_processed = []
    converted = []

    # Get currently selected books
    rows = ia.gui.library_view.selectionModel().selectedRows()
    if not rows or len(rows) == 0:
        return error_dialog(ia.gui, _L['Cannot update metadata'],
                        _L['No books selected'], show=True)
    # Map the rows to book ids
    ids = list(map(ia.gui.library_view.model().id, rows))

    # iterate through the books
    for book_id in ids:
        metadata = ComicMetadata(book_id, ia)

        # sanity check
        if metadata.format is None:
            not_processed.append(metadata.info)
            continue

        if convert:
            converted = convert_if_prefs(ia, convaction, metadata, converted)

        if func(metadata):
            processed.append(metadata.info)
        else:
            not_processed.append(metadata.info)

        # clean up
        metadata.delete_temp_cbz_file()

    msg = ptext.format(len(processed))
    if convert and len(converted) > 0:
        msg += '\n' + convtext.format(len(converted))
    if len(not_processed) > 0:
        msg += '\n' + notptext.format(len(not_processed))
    info_dialog(ia.gui, title, msg, show=True)


def convert_if_prefs(ia, action, metadata, converted):
    # check if we should convert
    if (prefs['convert_cbr'] and metadata.format == "cbr" and action == "convert_cbr") or (
            prefs['convert_reading'] and metadata.format == "cbr" and action == "convert_reading"):
        metadata.convert_to_cbz()
        converted.append(metadata.info)
        if prefs['delete_cbr']:
            ia.gui.current_db.new_api.remove_formats({metadata.book_id: {'cbr'}})
    return converted
