__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from calibre.utils.zipfile import ZipFile
from calibre.gui2 import error_dialog, info_dialog

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.genericmetadata import GenericMetadata


def update_metadata(ia, do_embed): 	# ia = interface action
	'''
	Redirects and handles the action indicated by "do_embed"
	The main function for the plugin
	'''

	# get the db from calibre, to get metadata etc
	ia.db = ia.gui.current_db.new_api

	# initialize some variables
	convert_cbr = prefs['convert_cbr']
	convert_reading = prefs['convert_reading']
	delete_cbr = prefs['delete_cbr']
	books_processed = []
	books_not_processed = []
	books_converted = []

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

		# generate a string with the books info, to show in the completion dialog
		book_info = str(calibre_metadata.title) + " - " + str(calibre_metadata.authors[0])
		if calibre_metadata.series:
			book_info = str(calibre_metadata.series) + ": " + str(calibre_metadata.series_index) + " - " + book_info

		# get the comic formats
		is_cbz_comic = ia.db.has_format(book_id, "cbz")
		is_cbr_comic = ia.db.has_format(book_id, "cbr")

		# sanity check
		if not is_cbz_comic and not is_cbr_comic:
			books_not_processed.append(book_info)
			continue

		# only convert cbr to cbz
		if do_embed == "just_convert":
			if not is_cbr_comic:
				books_not_processed.append(book_info)
				continue
			convert_cbr_to_cbz(ia, book_id, delete_cbr)
			books_converted.append(book_info)
			continue

		# read comic metadata and write to calibre
		if do_embed == "read_both" or do_embed == "read_cix" or do_embed == "read_cbi":
			# convert, if option is on
			if (convert_reading and is_cbr_comic and not is_cbz_comic):
				convert_cbr_to_cbz(ia, book_id, delete_cbr)
				books_converted.append(book_info)
				is_cbz_comic = True
			# write the metadat to calibres database
			has_updated = write_calibre_metadata(ia, do_embed, book_id, calibre_metadata, is_cbz_comic)
			if not has_updated:
				books_not_processed.append(book_info)
			else:
				books_processed.append(book_info)
			continue

		# convert to cbz if book has only cbr format and option is on
		if (convert_cbr and is_cbr_comic and not is_cbz_comic):
			convert_cbr_to_cbz(ia, book_id, delete_cbr)
			books_converted.append(book_info)
			is_cbz_comic = True

		# if the book is a cbz, embed the metadata in the cbz file
		if is_cbz_comic:
			embed_comic_metadata(ia, book_id, calibre_metadata, do_embed)
			books_processed.append(book_info)
		else:
			books_not_processed.append(book_info)

	# Show the completion dialog
	if do_embed == "just_convert":
		title = 'Converted files'
		msg = 'Converted {} book(s) to cbz'.format(len(books_converted))
		if len(books_not_processed) > 0:
			msg += '\nThe following books were not converted: {}'.format(books_not_processed)
	elif do_embed == "read_both" or do_embed == "read_cix" or do_embed == "read_cbi":
		title = 'Updated Calibre Metadata'
		msg = 'Updated calibre metadata for {} book(s)'.format(len(books_processed))
		if len(books_not_processed) > 0:
			msg += '\nThe following books had no metadata: {}'.format(books_not_processed)
	else:
		title = 'Updated files'
		msg = 'Updated the metadata in the files of {} book(s)'.format(len(books_processed))
		if len(books_converted) > 0:
			msg += '\nThe following books were converted to cbz: {}'.format(books_converted)
		if len(books_not_processed) > 0:
			msg += '\nThe following books were not updated: {}'.format(books_not_processed)

	info_dialog(ia.gui, title, msg, show=True)


def embed_comic_metadata(ia, book_id, calibre_metadata, do_embed):
	'''
	Set the metadata in the file to	match the current metadata in the database.
	'''

	# copy the file to temp folder
	ffile = ia.db.format(book_id, "cbz", as_path=True)

	# now copy the calibre metadata to comictagger compatible metadata
	overlay_metadata = get_overlay_metadata(calibre_metadata)

	# embed the comicinfo.xml
	if do_embed == "both" or do_embed == "cix":
		embed_cix_metadata(ffile, overlay_metadata)
	# embed the cbi metadata
	if do_embed == "both" or do_embed == "cbi":
		embed_cbi_metadata(ffile, overlay_metadata)

	# add the updated file to calibres library
	ia.db.add_format(book_id, "cbz", ffile)


def get_overlay_metadata(calibre_metadata):
	'''
	Copies calibres metadata to comictagger compatible metadata
	'''

	from calibre.utils.html2text import html2text
	from calibre.utils.date import UNDEFINED_DATE
	from calibre.utils.localization import lang_as_iso639_1

	overlay_metadata = GenericMetadata()

	if calibre_metadata.title:
		overlay_metadata.title = calibre_metadata.title
	if len(calibre_metadata.authors) > 0:
		for author in calibre_metadata.authors:
			credit = dict()
			credit['person'] = author
			credit['role'] = "Writer"
			overlay_metadata.credits.append(credit)
	if calibre_metadata.series:
		overlay_metadata.series = calibre_metadata.series
	if calibre_metadata.series_index:
		overlay_metadata.issue = int(calibre_metadata.series_index)
	if len(calibre_metadata.tags) > 0:
		overlay_metadata.tags = calibre_metadata.tags
	if calibre_metadata.publisher:
		overlay_metadata.publisher = calibre_metadata.publisher
	if calibre_metadata.comments:
		overlay_metadata.comments = html2text(calibre_metadata.comments)
	if calibre_metadata.pubdate != UNDEFINED_DATE:
		overlay_metadata.year = calibre_metadata.pubdate.year
		overlay_metadata.month = calibre_metadata.pubdate.month
		overlay_metadata.day = calibre_metadata.pubdate.day
	if calibre_metadata.language:
		overlay_metadata.language = lang_as_iso639_1(calibre_metadata.language)

	return overlay_metadata


def write_calibre_metadata(ia, do_embed, book_id, calibre_metadata, is_cbz_comic):
	'''
	Reads the comic metadata from the comic file and then writes the
	metadata into calibres database
	'''

	# if there is a cbz, take info from there, otherwise use the cbr
	if is_cbz_comic:
		ext = "cbz"
	else:
		ext = "cbr"
	# get the file
	ffile = ia.db.format(book_id, ext, as_path=True)
	# get the metadata from the file, depending on "do_embed". if both, prefer
	# "cix_metadata" (maybe make a preference later)
	comic_metadata = get_comic_metadata_from_file(ffile, ext, do_embed)

	# if no metadata return
	if comic_metadata is None:
		return False

	# update calibres metadata with the comic_metadata
	calibre_metadata = update_calibre_metadata(calibre_metadata, comic_metadata)
	# write the metadata to the database
	ia.db.set_metadata(book_id, calibre_metadata)

	return True


def update_calibre_metadata(calibre_metadata, comic_metadata):
	'''
	Maps the entries in the comic_metadata to calibre metadata
	'''

	# from calibre.utils.html2text import html2text
	# from calibre.utils.date import UNDEFINED_DATE
	# from calibre.utils.localization import lang_as_iso639_1

	if comic_metadata.title:
		calibre_metadata.title = comic_metadata.title
	# if len(comic_metadata.authors) > 0:
	# 	for author in comic_metadata.authors:
	# 		credit = dict()
	# 		credit['person'] = author
	# 		credit['role'] = "Writer"
	# 		calibre_metadata.credits.append(credit)
	if comic_metadata.series:
		calibre_metadata.series = comic_metadata.series
	if comic_metadata.issue:
		calibre_metadata.series_index = float(comic_metadata.issue)
	if len(comic_metadata.tags) > 0:
		calibre_metadata.tags = comic_metadata.tags
	if comic_metadata.publisher:
		calibre_metadata.publisher = comic_metadata.publisher
	# if comic_metadata.comments:
	# 	calibre_metadata.comments = html2text(comic_metadata.comments)
	# if comic_metadata.pubdate != UNDEFINED_DATE:
	# 	calibre_metadata.year = comic_metadata.pubdate.year
	# 	calibre_metadata.month = comic_metadata.pubdate.month
	# 	calibre_metadata.day = comic_metadata.pubdate.day
	# if comic_metadata.language:
	# 	calibre_metadata.language = lang_as_iso639_1(comic_metadata.language)

	return calibre_metadata


def embed_cix_metadata(ffile, overlay_metadata):
	from calibre_plugins.EmbedComicMetadata.comicinfoxml import ComicInfoXml

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

	# get the metadata to embed
	cix_metadata = get_metadata_string(cix_metadata, overlay_metadata,
					ComicInfoXml().metadataFromString, ComicInfoXml().stringFromMetadata)

	# save the metadata in the file
	if cix_file is not None:
		zf.replacestr(cix_file, cix_metadata)
	else:
		zf.writestr("ComicInfo.xml", cix_metadata)

	# close the zipfile
	zf.close()


def embed_cbi_metadata(ffile, overlay_metadata):
	from calibre_plugins.EmbedComicMetadata.comicbookinfo import ComicBookInfo

	# get cbi metadata from the zip comment
	zf = ZipFile(ffile)
	cbi_metadata = zf.comment
	zf.close()

	# get the metadata to embed
	cbi_metadata = get_metadata_string(cbi_metadata, overlay_metadata,
					ComicBookInfo().metadataFromString, ComicBookInfo().stringFromMetadata, ComicBookInfo().validateString)

	# save the metadata in the comment
	writeZipComment(ffile, cbi_metadata)


def get_metadata_string(metadata, overlay_metadata, fromString, toString, validate=None):
	'''
	Returns the metadata to be embedded as a string
	'''

	if validate is None:
		is_validated = True
	else:
		is_validated = validate(metadata)

	# transform the existing metadata to comictagger compatible metadata
	if metadata is None or not is_validated:
		metadata = GenericMetadata()
	else:
		metadata = fromString(metadata)

	# now overlay the calibre metadata with the original metadata
	metadata.overlay(overlay_metadata)

	# transform the metadata back to string
	return toString(metadata)


def convert_cbr_to_cbz(ia, book_id, delete_cbr):
	'''
	Converts a cbr-comic to a cbz-comic
	'''

	from calibre.ptempfile import TemporaryFile, TemporaryDirectory
	from calibre.utils.unrar import extract

	with TemporaryDirectory('_cbr2cbz') as tdir:
		# extract the rar file
		ffile = ia.db.format(book_id, "cbr", as_path=True)
		extract(ffile, tdir)

		# make the cbz file
		with TemporaryFile("comic.cbz") as tf:
			zf = ZipFile(tf, "w")
			zf.add_dir(tdir)
			zf.close()
			# add the cbz format to calibres library
			ia.db.add_format(book_id, "cbz", tf)
	if delete_cbr:
		ia.db.remove_formats({book_id: {'cbr'}})


def get_comic_metadata_from_file(ffile, ext, do_embed):
	'''
	Reads the comic metadata from the comic file as comictagger metadata
	and returns the metadata depending on do_embed
	'''

	from calibre_plugins.EmbedComicMetadata.comicinfoxml import ComicInfoXml
	from calibre_plugins.EmbedComicMetadata.comicbookinfo import ComicBookInfo

	cix_metadata = None
	cbi_metadata = None
	if ext == "cbz":
		# open the zipfile
		zf = ZipFile(ffile)
		# get cix metadata
		if do_embed == "read_both" or do_embed == "read_cix":
			for name in zf.namelist():
				if name.lower() == "comicinfo.xml":
					cix_metadata = zf.read(name)
		# get the cbi metadata
		if (do_embed == "read_both" and cix_metadata is None) or do_embed == "read_cbi":
			cbi_metadata = zf.comment
		zf.close()
	else:
		# get the cbi metadata
		from calibre.utils.unrar import RARFile
		zr = RARFile(ffile, get_comment=True)
		cbi_metadata = zr.comment

	# get the metadata as comictagger metadata
	if cix_metadata is not None:
		return ComicInfoXml().metadataFromString(cix_metadata)
	if cbi_metadata is not None and ComicBookInfo().validateString(cbi_metadata):
		return ComicBookInfo().metadataFromString(cbi_metadata)
	return None


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
