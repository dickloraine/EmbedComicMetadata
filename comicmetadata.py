__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from functools import partial
from calibre.utils.zipfile import ZipFile

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.utils import (update_comic_field,
    update_calibre_field, update_custom_column, get_role, set_role)
from calibre_plugins.EmbedComicMetadata.genericmetadata import GenericMetadata
from calibre_plugins.EmbedComicMetadata.comicinfoxml import ComicInfoXml
from calibre_plugins.EmbedComicMetadata.comicbookinfo import ComicBookInfo


class ComicMetadata:
    '''
    An object for calibre to interact with comic metadata.
    '''

    def __init__(self, book_id, ia):
        self.book_id = book_id
        self.ia = ia
        self.db = ia.gui.current_db.new_api

        # iniatialize the atributes
        self.calibre_metadata = self.db.get_metadata(book_id)
        self.cbi_metadata = None
        self.cix_metadata = None
        self.calibre_md_in_comic_format = None
        self.comic_md_in_calibre_format = None
        self.comic_metadata = None
        self.checked_for_metadata = False
        self.file = None
        self.zipinfo = None

        # get the comic formats
        if self.db.has_format(book_id, "cbz"):
            self.format = "cbz"
        elif self.db.has_format(book_id, "cbr"):
            self.format = "cbr"
        else:
            self.format = None

        # generate a string with the books info, to show in the completion dialog
        self.info = str(self.calibre_metadata.title) + " - " + str(self.calibre_metadata.authors[0])
        if self.calibre_metadata.series:
            self.info = (str(self.calibre_metadata.series) + ": " + str(self.calibre_metadata.series_index) +
                " - " + self.info)

    def get_comic_metadata_from_file(self):
        if self.checked_for_metadata:
            return
        if self.format == "cbz":
            self.get_comic_metadata_from_cbz()
        elif self.format == "cbr":
            self.get_comic_metadata_from_cbr()
        self.checked_for_metadata = True

    def add_updated_comic_to_calibre(self):
        self.db.add_format(self.book_id, "cbz", self.file)

    def import_comic_metadata_to_calibre(self, comic_metadata):
        self.convert_comic_md_to_calibre_md(comic_metadata)
        self.db.set_metadata(self.book_id, self.comic_md_in_calibre_format)

    def embed_cix_metadata(self):
        '''
        Embeds the cix_metadata
        '''
        # ensure we have a temp file
        self.make_temp_cbz_file()
        # make sure we have the metadata
        self.get_comic_metadata_from_file()
        # open the zipfile with append option
        zf = ZipFile(self.file, "a")
        # make the metadata generic, if none exists now
        if self.cix_metadata is None:
            self.cix_metadata = GenericMetadata()
        # convert calibre metadata to comic format
        self.convert_calibre_md_to_comic_md()
        # now overlay the calibre metadata with the original metadata
        self.cix_metadata.overlay(self.calibre_md_in_comic_format)
        # transform the metadata back to string
        cix_string = ComicInfoXml().stringFromMetadata(self.cix_metadata)
        # save the metadata in the file
        if self.zipinfo is not None:
            zf.replacestr(self.zipinfo, cix_string.decode('utf-8', 'ignore'))
        else:
            zf.writestr("ComicInfo.xml", cix_string.decode('utf-8', 'ignore'))
        # close the zipfile
        zf.close()

    def embed_cbi_metadata(self):
        '''
        Embeds the cbi_metadata
        '''
        from calibre_plugins.EmbedComicMetadata.utils import writeZipComment

        # ensure we have a temp file
        self.make_temp_cbz_file()
        # make sure we have the metadata
        self.get_comic_metadata_from_file()
        # make the metadata generic, if none exists now
        if self.cbi_metadata is None:
            self.cbi_metadata = GenericMetadata()
        # convert calibre metadata to comic format
        self.convert_calibre_md_to_comic_md()
        # now overlay the calibre metadata with the original metadata
        self.cbi_metadata.overlay(self.calibre_md_in_comic_format)
        # transform the metadata back to string
        cbi_string = ComicBookInfo().stringFromMetadata(self.cbi_metadata)
        # save the metadata in the comment
        writeZipComment(self.file, cbi_string)

    def convert_calibre_md_to_comic_md(self):
        '''
        Maps the entries in the calibre metadata to comictagger metadata
        '''
        from calibre.utils.html2text import html2text
        from calibre.utils.date import UNDEFINED_DATE
        from calibre.utils.localization import lang_as_iso639_1

        if self.calibre_md_in_comic_format:
            return

        self.calibre_md_in_comic_format = GenericMetadata()
        mi = self.calibre_metadata

        # shorten some functions
        role = partial(set_role, credits=self.calibre_md_in_comic_format.credits)
        update_field = partial(update_comic_field, target=self.calibre_md_in_comic_format)

        # update the fields of comic metadata
        update_field("title", mi.title)
        role("Writer", mi.authors)
        update_field("series", mi.series)
        update_field("issue", mi.series_index)
        update_field("tags", mi.tags)
        update_field("publisher", mi.publisher)
        update_field("criticalRating", mi.rating)
        # need to check for None
        if mi.comments:
            update_field("comments", html2text(mi.comments))
        if mi.language:
            update_field("language", lang_as_iso639_1(mi.language))
        if mi.pubdate != UNDEFINED_DATE:
            update_field("year", mi.pubdate.year)
            update_field("month", mi.pubdate.month)
            update_field("day", mi.pubdate.day)

        # custom columns
        field = partial(self.db.field_for, book_id=self.book_id)

        # artists
        role("Penciller", field(prefs['penciller_column']))
        role("Inker", field(prefs['inker_column']))
        role("Colorist", field(prefs['colorist_column']))
        role("Letterer", field(prefs['letterer_column']))
        role("CoverArtist", field(prefs['cover_artist_column']))
        role("Editor", field(prefs['editor_column']))
        # others
        update_field("storyArc", field(prefs['storyarc_column']))
        update_field("characters", field(prefs['characters_column']))
        update_field("teams", field(prefs['teams_column']))
        update_field("locations", field(prefs['locations_column']))
        update_field("volume", field(prefs['volume_column']))
        update_field("genre", field(prefs['genre_column']))

    def convert_comic_md_to_calibre_md(self, comic_metadata):
        '''
        Maps the entries in the comic_metadata to calibre metadata
        '''
        import unicodedata
        from calibre.ebooks.metadata import MetaInformation
        from calibre.utils.date import parse_only_date
        from datetime import date
        from calibre.utils.localization import calibre_langcode_to_name

        if self.comic_md_in_calibre_format:
            return

        # synonyms for artists
        WRITER = ['writer', 'plotter', 'scripter']
        PENCILLER = ['artist', 'penciller', 'penciler', 'breakdowns']
        INKER = ['inker', 'artist', 'finishes']
        COLORIST = ['colorist', 'colourist', 'colorer', 'colourer']
        LETTERER = ['letterer']
        COVER_ARTIST = ['cover', 'covers', 'coverartist', 'cover artist']
        EDITOR = ['editor']

        # start with a fresh calibre metadata
        mi = MetaInformation(None, None)
        co = comic_metadata

        # shorten some functions
        role = partial(get_role, credits=co.credits)
        update_field = partial(update_calibre_field, target=mi)

        # Get title, if no title, try to assign series infos
        if co.title:
            mi.title = co.title
        elif co.series:
            mi.title = co.series
            if co.issue:
                mi.title += " " + str(co.issue)
        else:
            mi.title = ""

        # simple metadata
        update_field("authors", role(WRITER))
        update_field("series", co.series)
        update_field("rating", co.criticalRating)
        update_field("publisher", co.publisher)
        # special cases
        if co.language:
            update_field("language", calibre_langcode_to_name(co.language))
        if co.comments:
            update_field("comments", co.comments.strip())
        # issue
        if co.issue:
            if isinstance(co.issue, unicode):
                mi.series_index = unicodedata.numeric(co.issue)
            else:
                mi.series_index = float(co.issue)
        # pub date
        puby = co.year
        pubm = co.month
        if puby is not None:
            try:
                dt = date(int(puby), 6 if pubm is None else int(pubm), 15)
                dt = parse_only_date(str(dt))
                mi.pubdate = dt
            except:
                pass

        # custom columns
        custom_cols = self.db.field_metadata.custom_field_metadata()
        update_column = partial(update_custom_column, calibre_metadata=mi, custom_cols=custom_cols)
        # artists
        update_column(prefs['penciller_column'], role(PENCILLER))
        update_column(prefs['inker_column'], role(INKER))
        update_column(prefs['colorist_column'], role(COLORIST))
        update_column(prefs['letterer_column'], role(LETTERER))
        update_column(prefs['cover_artist_column'], role(COVER_ARTIST))
        update_column(prefs['editor_column'], role(EDITOR))
        # others
        update_column(prefs['storyarc_column'], co.storyArc)
        update_column(prefs['characters_column'], co.characters)
        update_column(prefs['teams_column'], co.teams)
        update_column(prefs['locations_column'], co.locations)
        update_column(prefs['volume_column'], co.volume)
        update_column(prefs['genre_column'], co.genre)

        self.comic_md_in_calibre_format = mi

    def make_temp_cbz_file(self):
        if not self.file and self.format == "cbz":
            self.file = self.db.format(self.book_id, "cbz", as_path=True)

    def convert_to_cbz(self):
        '''
        Converts a cbr-comic to a cbz-comic
        '''
        from calibre.ptempfile import TemporaryFile, TemporaryDirectory
        from calibre.utils.unrar import RARFile, extract
        from calibre_plugins.EmbedComicMetadata.utils import writeZipComment

        with TemporaryDirectory('_cbr2cbz') as tdir:
            # extract the rar file
            ffile = self.db.format(self.book_id, "cbr", as_path=True)
            extract(ffile, tdir)
            # get the comment
            with open(ffile, 'rb') as stream:
                zr = RARFile(stream, get_comment=True)
                comment = zr.comment

            # make the cbz file
            with TemporaryFile("comic.cbz") as tf:
                zf = ZipFile(tf, "w")
                zf.add_dir(tdir)
                zf.close()
                # write comment
                if comment:
                    writeZipComment(tf, comment)
                # add the cbz format to calibres library
                self.db.add_format(self.book_id, "cbz", tf)
                self.format = "cbz"

    def update_cover(self):
        self.make_temp_cbz_file()
        # open the zipfile
        zf = ZipFile(self.file, "a")

        # get the calibre cover
        cover_path = self.db.cover(self.book_id, as_path=True)
        fmt = cover_path.rpartition('.')[-1]
        if fmt == "":
            zf.close()
            return False
        new_cover_name = "00000000_cover." + fmt

        # search for a previously embeded cover
        cover_info = ""
        for name in zf.namelist():
            if name.rsplit(".", 1)[0] == "00000000_cover":
                cover_info = name
                break

        # save the metadata in the file
        if cover_info != "":
            zf.delete(cover_info)
        zf.write(cover_path, new_cover_name)

        # close the zipfile
        zf.close()
        return True

    def get_comic_metadata_from_cbz(self):
        '''
        Reads the comic metadata from the comic cbz file as comictagger metadata
        '''
        self.make_temp_cbz_file()
        # open the zipfile
        zf = ZipFile(self.file)

        # get cix metadata
        for name in zf.namelist():
            if name.lower() == "comicinfo.xml":
                self.cix_metadata = ComicInfoXml().metadataFromString(zf.read(name))
                self.zipinfo = zf.getinfo(name)
                break

        # get the cbi metadata
        if ComicBookInfo().validateString(zf.comment):
            self.cbi_metadata = ComicBookInfo().metadataFromString(zf.comment)
        zf.close()

        # get combined metadata
        self._get_combined_metadata()

    def get_comic_metadata_from_cbr(self):
        '''
        Reads the comic metadata from the comic cbr file as comictagger metadata
        and returns the metadata depending on do_action
        '''
        from calibre.utils.unrar import RARFile, extract_member, names

        ffile = self.db.format(self.book_id, "cbr", as_path=True)
        with open(ffile, 'rb') as stream:
            # get the cix metadata
            fnames = list(names(stream))
            for name in fnames:
                if name.lower() == "comicinfo.xml":
                    self.cix_metadata = extract_member(stream, match=None, name=name)[1]
                    self.cix_metadata = ComicInfoXml().metadataFromString(self.cix_metadata)
                    break

            # get the cbi metadata
            zr = RARFile(stream, get_comment=True)
            comment = zr.comment
            if ComicBookInfo().validateString(comment):
                self.cbi_metadata = ComicBookInfo().metadataFromString(comment)

        self._get_combined_metadata()

    def _get_combined_metadata(self):
        '''
        Combines the metadata from both sources
        '''
        self.comic_metadata = GenericMetadata()
        if self.cbi_metadata is not None:
            self.comic_metadata.overlay(self.cbi_metadata, False)
        if self.cix_metadata is not None:
            self.comic_metadata.overlay(self.cix_metadata, False)
        if self.cbi_metadata is None and self.cix_metadata is None:
            self.comic_metadata = None


def numericalSort(value):
    import re

    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts
    