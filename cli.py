from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from calibre_plugins.EmbedComicMetadata.comicmetadata import ComicMetadata

def _embed_metadata_into_comic(metadata, embed_format):
    if metadata.format != "cbz":
        print("Error! Can only read cbz files!")
        return False

    metadata.overlay_metadata()
    if embed_format == "both" or embed_format == "cix":
        metadata.embed_cix_metadata()
    if embed_format == "both" or embed_format == "cbi":
        metadata.embed_cbi_metadata()
    metadata.add_updated_comic_to_calibre()
    return True


def _convert_to_cbz(db, metadata, convert_archives, delete_cbr):
    if metadata.format == "cbr" or (metadata.format == "rar" and convert_archives):
        metadata.convert_cbr_to_cbz()
        if delete_cbr:
            db.remove_formats({metadata.book_id: {"cbr", "rar"}})
        return True
    elif metadata.format == "zip" and convert_archives:
        metadata.convert_zip_to_cbz()
        if delete_cbr:
            db.remove_formats({metadata.book_id: {"zip"}})
        return True
    return False


def _run_func_and_convert_for_ids(db, ids, func, embed_format, should_convert, convert_archives, delete_cbr):
    if not ids or len(ids) == 0:
        print("no book ids were given")
        return

    # iterate through the books
    for book_id in ids:
        metadata = ComicMetadata(book_id, db)

        # sanity check
        if metadata.format is None:
            print("Following item was not processed (missing format): ", metadata.info)
            continue

        if should_convert and _convert_to_cbz(db, metadata, convert_archives, delete_cbr):
            print("Following item was converted: ", metadata.info)

        if func(metadata,embed_format):
            print("Successfully processed: ", metadata.info)
        else:
            print("Following item was not processed (process function failed): ", metadata.info)


def embed_and_maybe_convert(db, ids, embed_format="both", should_convert=False, convert_archives=False, delete_cbr=False):
    _run_func_and_convert_for_ids(db, ids, _embed_metadata_into_comic, embed_format, should_convert, convert_archives, delete_cbr)
