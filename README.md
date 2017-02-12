# Embed Comic Metadata

A Calibre Plugin to manage comic metadata in calibre

## Special Notes

Requires calibre version 1.0.0 or later.

## Main Features

- Can embed the metadata to the zip comment or a ComicInfo.xml file inside the archives
- Can read the above metadata formats and import them into calibre
- Can write many additional metadata into custom columns Can automatically convert cbr/zip/rar files to cbz
- Can embed the calibre cover into cbz comics (experimental)
- Can count the number of pages (image files) in a comic

## Usage

### To embed calibres metadata into the comic archive:

- Select the comics that should be updated in the library.
- Click the addon EmbedComicMetadata icon in your toolbar
- (You can select a specific action or open the configuration bei clicking on the small arrow on the icon and selecting the desired option)

### To import the comic archive metadata into calibre:

- Select the comics that should be updated in the library.
- Click the small arrow on the addon EmbedComicMetadata icon in your toolbar
- Click on "Import Metadata from the comic archive into calibre"

### Custom Columns:

You can make custom columns in calibre and populate them with metadata imported with the plugin. In the configuration use the dropdown menu for the columns to select what metadata should be written to what custom column.

The custom columns you make in calibre should be of the following type, depending on the metadata stored in them.

#### Comma seperated text, like tags, shown in the tag browser with "Contains names" checked:

Penciller, Inker, Colorist, Letterer, Cover Artist, Editor

#### Comma seperated text, like tags, shown in the tag browser:

Characters, Teams, Locations, Genre

#### Text, column shown in the tag browser:

Story Arc, Volume, Number of Issues

#### Integer:

Number of Issues, Volume

#### Series like:

Story Arc

#### Comment:

Comic Vine Link

### Customizing the main menu:

The menu in the toolbar can be custimized to your liking through the options in the configuration.

### Embed Cover:

Use with care, just inserts the calibre cover as "00000000_cover" into the comic archive (previously inserted calibre covers are overwritten).

## Configuration

- **Write metadata in zip comment**: This format is used by calibre, if you import comic files and by ComicbookLovers (default: on)
- **Write metadata in ComicInfo.xml**: This format is used by ComicRack and some other comic readers (default: on)
- **Auto convert cbr to cbz**: If a comic has only the cbr format, convert it to store the metadata (default: on)
- **Also convert rar and zip to cbz**: Expand the behaviour for cbr to rars and zips (default: off)
- **Auto convert while importing to calibre**: As above, but even when importing metadata into calibre (default: off)
- **Delete cbr after conversion**: Deletes the cbr format after the conversion (default: off)
- **Swap names to "LN, FN" when importing metadata**: Does just what it says (default: off)
- **Auto count pages if importing**: Count pages automatically if importing metadata into calibre (default: off)
- **Main Button Action**: You can set, what action should be performed if the big toolbar button is pressed. Needs a calibre restart (default: Embed metadata)
- **Menu Buttons**: The dropdown menu on the icon in the toolbar can be custimized to your liking through these options

## Acknowledgement

The handling of the comic metadata is done by using code from [ComicTagger](https://code.google.com/p/comictagger/)
