__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from calibre.utils.zipfile import ZipFile
from calibre.ebooks.metadata import MetaInformation
from calibre.gui2 import error_dialog, info_dialog
from calibre.utils.html2text import html2text
from calibre.utils.date import UNDEFINED_DATE
from calibre.utils.localization import lang_as_iso639_1

from calibre_plugins.EmbedComicMetadata.config import prefs
from calibre_plugins.EmbedComicMetadata.comicinfoxml import ComicInfoXml
from calibre_plugins.EmbedComicMetadata.comicbookinfo import ComicBookInfo
from calibre_plugins.EmbedComicMetadata.genericmetadata import GenericMetadata
from calibre_plugins.EmbedComicMetadata.utils import writeZipComment


def update_metadata(ia, do_embed):	#ia = interface action
	'''
	Set the metadata in the files in the selected comic's records to
	match the current metadata in the database.
	'''	
	
	# get the db from calibre, to get metadata etc
	ia.db = ia.gui.current_db.new_api
	
	# initialize some variables
	convert_cbr = prefs['convert_cbr']
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
		
		# only convert cbr to cbz 
		if do_embed == "just_convert":
			if not is_cbr_comic:
				books_not_processed.append(book_info)
				continue
			convert_cbr_to_cbz(ia, book_id)
			if delete_cbr:
				ia.db.remove_formats({book_id:{'cbr'}})
			books_converted.append(book_info)
			continue
		
		# convert to cbz if book has only cbr format and option is on
		if convert_cbr and is_cbr_comic and not is_cbz_comic:
			convert_cbr_to_cbz(ia, book_id)
			if delete_cbr:
				ia.db.remove_formats({book_id:{'cbr'}})
			books_converted.append(book_info)
			is_cbz_comic = True
			
		# embed the metadata, if the book is a cbz file
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
	Embeds the metadata in the given book
	'''
	
	# copy the file to temp folder
	ffile = ia.db.format(book_id, "cbz", as_path=True)
			
	# now copy the calibre metadata to comictagger compatible metadata
	overlay_metadata = get_overlay_metadata(calibre_metadata)
	
	# process cix metadata
	if do_embed == "both" or do_embed == "cix":
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
			
	# process cbi metadata
	if do_embed == "both" or do_embed == "cbi":
		# get cbi metadata from the zip comment
		zf = ZipFile(ffile)
		cbi_metadata = zf.comment	
		zf.close()
		
		# get the metadata to embed
		cbi_metadata = get_metadata_string(cbi_metadata, overlay_metadata,
						ComicBookInfo().metadataFromString, ComicBookInfo().stringFromMetadata, ComicBookInfo().validateString)	
		
		# save the metadata in the comment
		writeZipComment(ffile, cbi_metadata)

	# add the updated file to calibres library
	ia.db.add_format(book_id, "cbz", ffile)	

	
def get_overlay_metadata(calibre_metadata):
	'''
	Copies calibres metadata to comictagger compatible metadata
	'''
	
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
	
def convert_cbr_to_cbz(ia, book_id):
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