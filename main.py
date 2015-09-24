__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from functools import partial
from calibre.utils.zipfile import ZipFile
from calibre.gui2 import error_dialog, info_dialog

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.genericmetadata import GenericMetadata
from calibre_plugins.EmbedComicMetadata.comicinfoxml import ComicInfoXml
from calibre_plugins.EmbedComicMetadata.comicbookinfo import ComicBookInfo


def update_metadata(ia, do_action): 	# ia = interface action
	'''
	Redirects and handles the action indicated by "do_action"
	The main function for the plugin
	'''
	# get the db from calibre, to get metadata etc
	ia.db = ia.gui.current_db.new_api

	# initialize j(ob), to store all needed informations
	j = {"BOOK_ID": 0, "FORMAT": "", "INFO": "", "ACTION": do_action,
		"PROCESSED": [], "NOT_PROCESSED": [], "CONVERTED": []}

	# Get currently selected books
	rows = ia.gui.library_view.selectionModel().selectedRows()
	if not rows or len(rows) == 0:
		return error_dialog(ia.gui, 'Cannot update metadata',
						'No books selected', show=True)
	# Map the rows to book ids
	ids = list(map(ia.gui.library_view.model().id, rows))

	# iterate through the books
	for book_id in ids:
		# Get the current metadata for this book from the db
		calibre_metadata = ia.db.get_metadata(book_id)

		# save book_id in j
		j["BOOK_ID"] = book_id

		# generate a string with the books info, to show in the completion dialog
		j["INFO"] = str(calibre_metadata.title) + " - " + str(calibre_metadata.authors[0])
		if calibre_metadata.series:
			j["INFO"] = (str(calibre_metadata.series) + ": " + str(calibre_metadata.series_index) +
				" - " + j["INFO"])

		# get the comic formats
		if ia.db.has_format(book_id, "cbz"):
			j["FORMAT"] = "cbz"
		elif ia.db.has_format(book_id, "cbr"):
			j["FORMAT"] = "cbr"
		else:
			j["NOT_PROCESSED"].append(j["INFO"])
			continue

		# only convert cbr to cbz
		if j["ACTION"] == "just_convert":
			convert_cbr_to_cbz(ia, j)
			continue

		# read comic metadata and write to calibre
		if j["ACTION"] == "read_both" or j["ACTION"] == "read_cix" or j["ACTION"] == "read_cbi":
			# write the metadata to calibres database
			write_calibre_metadata(ia, j)
			continue

		# embed the calibre metadata into the comic archive
		embed_comic_metadata(ia, j, calibre_metadata)

	# Show the completion dialog
	if j["ACTION"] == "just_convert":
		title = 'Converted files'
		msg = 'Converted {} book(s) to cbz'.format(len(j["CONVERTED"]))
		if len(j["NOT_PROCESSED"]) > 0:
			msg += '\nThe following books were not converted: {}'.format(j["NOT_PROCESSED"])
	elif j["ACTION"] == "read_both" or j["ACTION"] == "read_cix" or j["ACTION"] == "read_cbi":
		title = 'Updated Calibre Metadata'
		msg = 'Updated calibre metadata for {} book(s)'.format(len(j["PROCESSED"]))
		if len(j["NOT_PROCESSED"]) > 0:
			msg += '\nThe following books had no metadata: {}'.format(j["NOT_PROCESSED"])
	else:
		title = 'Updated files'
		msg = 'Updated the metadata in the files of {} book(s)'.format(len(j["PROCESSED"]))
		if len(j["CONVERTED"]) > 0:
			msg += '\nThe following books were converted to cbz: {}'.format(j["CONVERTED"])
		if len(j["NOT_PROCESSED"]) > 0:
			msg += '\nThe following books were not updated: {}'.format(j["NOT_PROCESSED"])
	info_dialog(ia.gui, title, msg, show=True)


def embed_comic_metadata(ia, j, calibre_metadata):
	'''
	Set the metadata in the file to	match the current metadata in the database.
	'''
	# convert if option is on
	if prefs['convert_cbr']:
		convert_cbr_to_cbz(ia, j)

	# if not a cbz return
	if j["FORMAT"] != "cbz":
		j["NOT_PROCESSED"].append(j["INFO"])
		return

	# copy the file to temp folder
	ffile = ia.db.format(j["BOOK_ID"], "cbz", as_path=True)

	# now copy the calibre metadata to comictagger compatible metadata
	overlay_metadata = get_overlay_metadata(ia, j, calibre_metadata)

	# embed the comicinfo.xml
	if j["ACTION"] == "both" or j["ACTION"] == "cix":
		embed_cix_metadata(ffile, overlay_metadata)

	# embed the cbi metadata
	if j["ACTION"] == "both" or j["ACTION"] == "cbi":
		embed_cbi_metadata(ffile, overlay_metadata)

	# add the updated file to calibres library
	ia.db.add_format(j["BOOK_ID"], "cbz", ffile)
	j["PROCESSED"].append(j["INFO"])


def get_overlay_metadata(ia, j, calibre_metadata):
	'''
	Copies calibres metadata to comictagger compatible metadata
	'''
	from calibre.utils.html2text import html2text
	from calibre.utils.date import UNDEFINED_DATE
	from calibre.utils.localization import lang_as_iso639_1

	overlay_metadata = GenericMetadata()

	role = partial(set_role, credits=overlay_metadata.credits)
	update_field = partial(update_comic_field, target=overlay_metadata)

	update_field("title", calibre_metadata.title)
	role("Writer", calibre_metadata.authors)
	update_field("series", calibre_metadata.series)
	update_field("issue", calibre_metadata.series_index)
	update_field("tags", calibre_metadata.tags)
	update_field("publisher", calibre_metadata.publisher)
	update_field("criticalRating", calibre_metadata.rating)
	# need to check for None
	if calibre_metadata.comments:
		update_field("comments", html2text(calibre_metadata.comments))
	if calibre_metadata.language:
		update_field("language", lang_as_iso639_1(calibre_metadata.language))
	if calibre_metadata.pubdate != UNDEFINED_DATE:
		update_field("year", calibre_metadata.pubdate.year)
		update_field("month", calibre_metadata.pubdate.month)
		update_field("day", calibre_metadata.pubdate.day)

	# custom columns
	field = partial(ia.db.field_for, book_id=j["BOOK_ID"])

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

	return overlay_metadata


def write_calibre_metadata(ia, j):
	'''
	Reads the comic metadata from the comic file and then writes the
	metadata into calibres database
	'''
	# convert, if option is on
	if prefs['convert_reading']:
		convert_cbr_to_cbz(ia, j)

	# get the metadata from the comic archive
	comic_metadata = get_comic_metadata_from_file(ia, j)

	# if no metadata return
	if comic_metadata is None:
		j["NOT_PROCESSED"].append(j["INFO"])
		return

	# update calibres metadata with the comic_metadata
	calibre_metadata = update_calibre_metadata(ia, comic_metadata)

	# write the metadata to the database
	ia.db.set_metadata(j["BOOK_ID"], calibre_metadata)
	j["PROCESSED"].append(j["INFO"])


def update_calibre_metadata(ia, comic_metadata):
	'''
	Maps the entries in the comic_metadata to calibre metadata
	'''
	import unicodedata
	from calibre.ebooks.metadata import MetaInformation
	from calibre.utils.date import parse_only_date
	from datetime import date
	from calibre.utils.localization import calibre_langcode_to_name

	# synonyms for artists
	WRITER = ['writer', 'plotter', 'scripter']
	PENCILLER = ['artist', 'penciller', 'penciler', 'breakdowns']
	INKER = ['inker', 'artist', 'finishes']
	COLORIST = ['colorist', 'colourist', 'colorer', 'colourer']
	LETTERER = ['letterer']
	COVER_ARTIST = ['cover', 'covers', 'coverartist', 'cover artist']
	EDITOR = ['editor']

	# start with a fresh calibre metadata
	calibre_metadata = MetaInformation(None, None)

	role = partial(get_role, credits=comic_metadata.credits)
	update_field = partial(update_calibre_field, target=calibre_metadata)

	# Get title, if no title, try to assign series infos
	update_field("title", comic_metadata.title)
	if not comic_metadata.title:
		# try to find a series
		if comic_metadata.series:
			calibre_metadata.title = comic_metadata.series
			if comic_metadata.issue:
				calibre_metadata.title += " " + str(comic_metadata.issue)
		else:
			calibre_metadata.title = ""

	# simple metadata
	update_field("authors", role(WRITER))
	update_field("series", comic_metadata.series)
	update_field("rating", comic_metadata.criticalRating)
	update_field("publisher", comic_metadata.publisher)
	# special cases
	if comic_metadata.language:
		update_field("language", calibre_langcode_to_name(comic_metadata.language))
	if comic_metadata.comments:
		update_field("comments", comic_metadata.comments.strip())
	# issue
	if comic_metadata.issue:
		if isinstance(comic_metadata.issue, unicode):
			calibre_metadata.series_index = unicodedata.numeric(comic_metadata.issue)
		else:
			calibre_metadata.series_index = float(comic_metadata.issue)
	# pub date
	puby = comic_metadata.year
	pubm = comic_metadata.month
	if puby is not None:
		try:
			dt = date(puby, 6 if pubm is None else pubm, 15)
			dt = parse_only_date(str(dt))
			calibre_metadata.pubdate = dt
		except:
			pass

	# custom columns
	custom_cols = ia.db.field_metadata.custom_field_metadata()
	update_column = partial(update_custom_column, calibre_metadata=calibre_metadata, custom_cols=custom_cols)
	# artists
	update_column(prefs['penciller_column'], role(PENCILLER))
	update_column(prefs['inker_column'], role(INKER))
	update_column(prefs['colorist_column'], role(COLORIST))
	update_column(prefs['letterer_column'], role(LETTERER))
	update_column(prefs['cover_artist_column'], role(COVER_ARTIST))
	update_column(prefs['editor_column'], role(EDITOR))
	# others
	update_column(prefs['storyarc_column'], comic_metadata.storyArc)
	update_column(prefs['characters_column'], comic_metadata.characters)
	update_column(prefs['teams_column'], comic_metadata.teams)
	update_column(prefs['locations_column'], comic_metadata.locations)
	update_column(prefs['volume_column'], comic_metadata.volume)
	update_column(prefs['genre_column'], comic_metadata.genre)

	return calibre_metadata


def embed_cix_metadata(ffile, overlay_metadata):
	'''
	Embeds the cix_metadata into the given file,
	overlayed with overlay_metadata
	'''
	# open the zipfile with append option
	zf = ZipFile(ffile, "a")

	# look for an existing comicinfo file
	cix_file = None
	cix_metadata = None
	for name in zf.namelist():
		if name.lower() == "comicinfo.xml":
			cix_file = zf.getinfo(name)
			cix_metadata = zf.read(name)
			break

	# transform the existing metadata to comictagger compatible metadata
	if cix_metadata is None:
		cix_metadata = GenericMetadata()
	else:
		cix_metadata = ComicInfoXml().metadataFromString(cix_metadata)

	# now overlay the calibre metadata with the original metadata
	cix_metadata.overlay(overlay_metadata)

	# transform the metadata back to string
	cix_metadata = ComicInfoXml().stringFromMetadata(cix_metadata)

	# save the metadata in the file
	if cix_file is not None:
		zf.replacestr(cix_file, cix_metadata)
	else:
		zf.writestr("ComicInfo.xml", cix_metadata)

	# close the zipfile
	zf.close()


def embed_cbi_metadata(ffile, overlay_metadata):
	'''
	Embeds the cbi_metadata into the given file,
	overlayed with overlay_metadata
	'''
	# get cbi metadata from the zip comment
	zf = ZipFile(ffile)
	cbi_metadata = zf.comment
	zf.close()

	# transform the existing metadata to comictagger compatible metadata
	if cbi_metadata is None or not ComicBookInfo().validateString(cbi_metadata):
		cbi_metadata = GenericMetadata()
	else:
		cbi_metadata = ComicBookInfo().metadataFromString(cbi_metadata)

	# now overlay the calibre metadata with the original metadata
	cbi_metadata.overlay(overlay_metadata)

	# transform the metadata back to string
	cbi_metadata = ComicBookInfo().stringFromMetadata(cbi_metadata)

	# save the metadata in the comment
	writeZipComment(ffile, cbi_metadata)


def get_comic_metadata_from_file(ia, j):
	if j["FORMAT"] == "cbz":
		return get_comic_metadata_from_cbz(ia, j)
	else:
		return get_comic_metadata_from_cbr(ia, j)


def get_comic_metadata_from_cbz(ia, j):
	'''
	Reads the comic metadata from the comic cbz file as comictagger metadata
	and returns the metadata depending on do_action
	'''
	cix_metadata = None
	cbi_metadata = None
	ffile = ia.db.format(j["BOOK_ID"], "cbz", as_path=True)
	# open the zipfile
	zf = ZipFile(ffile)

	# get cix metadata
	if j["ACTION"] == "read_both" or j["ACTION"] == "read_cix":
		for name in zf.namelist():
			if name.lower() == "comicinfo.xml":
				cix_metadata = ComicInfoXml().metadataFromString(zf.read(name))
				break

	# get the cbi metadata
	if (j["ACTION"] == "read_both" or j["ACTION"] == "read_cbi") and (
				ComicBookInfo().validateString(zf.comment)):
		cbi_metadata = ComicBookInfo().metadataFromString(zf.comment)
	zf.close()
	return get_combined_metadata(cix_metadata, cbi_metadata)


def get_comic_metadata_from_cbr(ia, j):
	'''
	Reads the comic metadata from the comic cbr file as comictagger metadata
	and returns the metadata depending on do_action
	'''
	from calibre.utils.unrar import RARFile, extract_member, names

	cix_metadata = None
	cbi_metadata = None
	ffile = ia.db.format(j["BOOK_ID"], "cbr", as_path=True)
	with open(ffile, 'rb') as stream:
		# get the cix metadata
		if j["ACTION"] == "read_both" or j["ACTION"] == "read_cix":
			fnames = list(names(stream))
			for name in fnames:
				if name.lower() == "comicinfo.xml":
					cix_metadata = extract_member(stream, match=None, name=name)[1]
					cix_metadata = ComicInfoXml().metadataFromString(cix_metadata)
					break

		# get the cbi metadata
		zr = RARFile(stream, get_comment=True)
		comment = zr.comment
		if (j["ACTION"] == "read_both" or j["ACTION"] == "read_cbi") and (
					ComicBookInfo().validateString(comment)):
			cbi_metadata = ComicBookInfo().metadataFromString(comment)
	return get_combined_metadata(cix_metadata, cbi_metadata)


def get_combined_metadata(cix_metadata, cbi_metadata):
	'''
	Combines the metadata from both sources
	'''
	if cix_metadata is not None and cbi_metadata is not None:
		cbi_metadata.overlay(cix_metadata, False)
		return cbi_metadata
	elif cix_metadata is not None:
		return cix_metadata
	return cbi_metadata


def update_comic_field(field, source, target):
	if source:
		setattr(target, field, source)


def update_calibre_field(field, source, target):
	if source:
		target.set(field, source)


def update_custom_column(col_name, value, calibre_metadata, custom_cols):
	if col_name and value:
		col = custom_cols[col_name]
		col['#value#'] = value
		calibre_metadata.set_user_metadata(col_name, col)


def get_role(role, credits):
	'''
	Gets a list of persons with the given role.
	First primary persons, then all others, alphabetically
	'''
	persons = []
	for credit in credits:
		if credit['role'].lower() in role:
			persons.append(credit['person'])
	persons.sort()
	return persons


def set_role(role, persons, credits):
	if persons and len(persons) > 0:
		for person in persons:
			credit = dict()
			credit['person'] = person
			credit['role'] = role
			credits.append(credit)


def convert_cbr_to_cbz(ia, j):
	'''
	Converts a cbr-comic to a cbz-comic
	'''
	from calibre.ptempfile import TemporaryFile, TemporaryDirectory
	from calibre.utils.unrar import RARFile, extract

	if j["FORMAT"] == "cbz":
		if j["ACTION"] == "just_convert":
			j["NOT_PROCESSED"].append(j["INFO"])
		return

	with TemporaryDirectory('_cbr2cbz') as tdir:
		# extract the rar file
		ffile = ia.db.format(j["BOOK_ID"], "cbr", as_path=True)
		extract(ffile, tdir)
		# get the comment
		with open(ffile, 'rb') as stream:
			zr = RARFile(stream, get_comment=True)
			comment = zr.comment

		# make the cbz file
		with TemporaryFile("comic.cbz") as tf:
			zf = ZipFile(tf, "w")
			zf.add_dir(tdir)
			if comment:
				zf.comment = comment
			zf.close()
			# add the cbz format to calibres library
			ia.db.add_format(j["BOOK_ID"], "cbz", tf)

	if prefs['delete_cbr']:
		ia.db.remove_formats({j["BOOK_ID"]: {'cbr'}})

	j["FORMAT"] = "cbz"
	j["CONVERTED"].append(j["INFO"])


def writeZipComment(filename, comment):
	'''
	This is a custom function for writing a comment to a zip file,
	since the built-in one doesn't seem to work on Windows and Mac OS/X

	Fortunately, the zip comment is at the end of the file, and it's
	easy to manipulate.  See this website for more info:
	see: http://en.wikipedia.org/wiki/Zip_(file_format)#Structure
	'''
	from os import stat
	from struct import pack

	# get file size
	statinfo = stat(filename)
	file_length = statinfo.st_size

	try:
		fo = open(filename, "r+b")

		# the starting position, relative to EOF
		pos = -4

		found = False
		value = bytearray()

		# walk backwards to find the "End of Central Directory" record
		while (not found) and (-pos != file_length):
			# seek, relative to EOF
			fo.seek(pos, 2)

			value = fo.read(4)

			# look for the end of central directory signature
			if bytearray(value) == bytearray([0x50, 0x4b, 0x05, 0x06]):
				found = True
			else:
				# not found, step back another byte
				pos = pos - 1
			# print pos,"{1} int: {0:x}".format(bytearray(value)[0], value)

		if found:

			# now skip forward 20 bytes to the comment length word
			pos += 20
			fo.seek(pos, 2)

			# Pack the length of the comment string
			format = "H"                   # one 2-byte integer
			comment_length = pack(format, len(comment))  # pack integer in a binary string

			# write out the length
			fo.write(comment_length)
			fo.seek(pos + 2, 2)

			# write out the comment itself
			fo.write(comment)
			fo.truncate()
			fo.close()
		else:
			raise Exception('Failed to write comment to zip file!')
	except:
		return False
	else:
		return True
