__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'


def update_comic_field(field, source, target):
    '''
    Sets the attribute field of target to the value of source
    '''
    if source:
        setattr(target, field, source)


def update_calibre_field(field, source, target):
    '''
    Sets the attribute field of target to the value of source
    '''
    if source:
        target.set(field, source)


def update_custom_column(col_name, value, calibre_metadata, custom_cols):
    '''
    Updates the given custom column with the name of col_name to value
    '''
    if col_name and value:
        col = custom_cols[col_name]
        col['#value#'] = value
        calibre_metadata.set_user_metadata(col_name, col)


def get_role(role, credits):
    '''
    Gets a list of persons with the given role.
    First primary persons, then all others, alphabetically
    '''
    from calibre_plugins.EmbedComicMetadata.config import prefs

    persons = []
    for credit in credits:
        if credit['role'].lower() in role:
            persons.append(credit['person'])
    if prefs['swap_names']:
        persons = swap_authors_names(persons)
    return persons


def set_role(role, persons, credits):
    '''
    Sets all persons with the given role to credits
    '''
    if persons and len(persons) > 0:
        for person in persons:
            credit = dict()
            person = swap_author_names_back(person)
            credit['person'] = person
            credit['role'] = role
            credits.append(credit)


def swap_authors_names(authors):
    '''
    Swaps the names of all names in authors to "LN, FN"
    '''
    swaped_authors = []
    for author in authors:
        author = swap_author_names(author)
        swaped_authors.append(author)
    return swaped_authors


def swap_author_names(author):
    '''
    Swaps the name of the given author to "LN, FN"
    '''
    if author is None:
        return author
    if ',' in author:
        return author
    parts = author.split(None)
    if len(parts) <= 1:
        return author
    surname = parts[-1]
    return '%s, %s' % (surname, ' '.join(parts[:-1]))


def swap_author_names_back(author):
    if author is None:
        return author
    if ',' in author:
        parts = author.split(',')
        if len(parts) <= 1:
            return author
        surname = parts[0]
        return '%s %s' % (' '.join(parts[1:]), surname)
    return author


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
