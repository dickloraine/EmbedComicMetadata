# coding=utf-8

"""
Some generic utilities
"""

"""
Copyright 2012-2014  Anthony Beville

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
	
	
def listToString( l ):
	string = ""
	if l is not None:
		for item in l:
			if len(string) > 0:
				string += ", "
			string += item 
	return string
	

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
	
	#get file size
	statinfo = stat(filename)
	file_length = statinfo.st_size

	try:
		fo = open(filename, "r+b")

		#the starting position, relative to EOF
		pos = -4

		found = False
		value = bytearray()
	
		# walk backwards to find the "End of Central Directory" record
		while ( not found ) and ( -pos != file_length ):
			# seek, relative to EOF	
			fo.seek( pos,  2)

			value = fo.read( 4 )

			#look for the end of central directory signature
			if bytearray(value) == bytearray([ 0x50, 0x4b, 0x05, 0x06 ]):
				found = True
			else:
				# not found, step back another byte
				pos = pos - 1
			#print pos,"{1} int: {0:x}".format(bytearray(value)[0], value)
		
		if found:
			
			# now skip forward 20 bytes to the comment length word
			pos += 20
			fo.seek( pos,  2)

			# Pack the length of the comment string
			format = "H"                   # one 2-byte integer
			comment_length = pack(format, len(comment)) # pack integer in a binary string
			
			# write out the length
			fo.write( comment_length )
			fo.seek( pos+2,  2)
			
			# write out the comment itself
			fo.write( comment )
			fo.truncate()
			fo.close()
		else:
			raise Exception('Failed to write comment to zip file!')
	except:
		return False
	else:
		return True