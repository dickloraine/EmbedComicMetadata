# Embed Comic Metadata
A Calibre Plugin to embed calibres metadata into cbz comic archives

##Special Notes
Requires calibre version 1.0.0 or later.

##Main Features
Can embed the metadata to the zip comment or a ComicInfo.xml file inside the archives
Can automatically convert cbr files to cbz

##Usage
* Select the comics that should be updated in the library.
* Click the addon EmbedComicMetadata icon in your toolbar
* (You can select a specific action or open the configuration bei clicking on the small arrow on the icon and selecting the desired option)
* Done

##Configuration
* 'Write metadata in zip comment': This format is used by calibre, if you import comic files and by ComicbookLovers (default: on)
* 'Write metadata in ComicInfo.xml': This format is used by ComicRack and some other comic readers (default: on)
* 'Auto convert cbr to cbz': If a comic has only the cbr format, convert it to store the metadata (default: on)
* 'Delete cbr after conversion': Deletes the cbr format after the conversion (default: off)

##Acknowledgement
The handling of the comic metadata is done by using code from https://code.google.com/p/comictagger/
