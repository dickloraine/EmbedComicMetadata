__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext es'

es = {
    # CONFIG MENU
    # custom columns (ini.py)
    'Artists Custom Columns:': 'Columnas personalizadas de artistas:',
    'Other Custom Columns:': 'Otras columnas personalizadas:',
    'Penciller:': 'Dibujante:',
    'Inker:': 'Entintador:',
    'Colorist:': 'Colorista:',
    'Letterer:': 'Rotulador:',
    'Cover Artist:': 'Artista de portada:',
    'Editor:': 'Editor:',
    'Story Arc:': 'Arco narrativo:',
    'Characters:': 'Caracteres:',
    'Teams:': 'Equipos:',
    'Locations:': 'Ubicaciones:',
    'Volume:': 'Volumen:',
    'Genre:': 'Género:',
    'Number of issues:': 'Número de volumenes:',
    'Pages:': 'Páginas:',
    'Image size:': 'Tamaño Imagen:',
    'Comicvine link:': 'Comicvine enlace:',
    'Manga:': 'Manga:',
    # options (ini.py)
    "Options:": "Opciones:",
    'Write metadata in zip comment': 'Escribir metadatos en comentario zip',
    'Write metadata in ComicInfo.xml': 'Escribir metadatos en ComicInfo.xml',
    'Import metadata from zip comment': 'Importar metadatos desde comentario zip',
    'Import metadata from ComicInfo.xml': 'Importar metadatos desde Comicinfo.xml',
    'Auto convert cbr to cbz': 'Conversión automática de cbr a cbz',
    'Also convert rar and zip to cbz': 'También convierta rar y zip a cbz',
    'Auto convert while importing to calibre': 'Conversión automática al importar a calibre',
    'Delete cbr after conversion': 'Eliminar cbr después de la conversión',
    'Swap names to "LN, FN" when importing metadata': 'Cambie los nombres a "LN, FN" al importar metadatos',
    'Import tags from comic metadata': 'Importar etiquetas de metadatos de cómics',
    'If checked, overwrites the tags in calibre.': 'Si está marcado, sobrescribe las etiquetas en calibre.',
    'Auto count pages if importing': 'Conteo automático de páginas si se importa',
    'Get the image size if importing': 'Obtenga el tamaño de la imagen si la importa',
    # main_buton (ini.py)
    "Main Button Action (needs a calibre restart):": "Acción del botón principal (necesita reiniciar calibre):",
    'Embed metadata': 'Insertar metadatos',
    'Import metadata': 'Importar metadatatos',
    # toolbar_buttons (ini.py)
    "Menu Buttons:": "Botones de menú:",
    'Show embed both button': 'Mostrar botón para insertar ambos',
    'Show embed cbi button': 'Mostrar botón insertar cbi',
    'Show embed cix button': 'Mostrar botón insertar cix',
    'Show import both button': 'Mostrar botón importar ambos',
    'Show import cix button': 'Mostrar botón importar cix',
    'Show import cbi button': 'Mostrar botón importar cbi',
    'Show convert button': 'Mostrar botón de conversión',
    'Show embed cover button (experimental)': 'Mostrar botón para insertar portada (experimental)',
    'Show count pages button': 'Botón Mostrar recuento de páginas',
    'Show get image size button': 'Mostrar botón para obtener tamaño de imagen',
    'Show remove metadata button': 'Mostrar el botón para eliminar metadatos',

    # TOOLBAR MENU
    # (ini.py)
    'Import Metadata from the comic archive into calibre': 'Importar metadatos del archivo de cómics a calibre',
    "Import Comic Rack Metadata from the comic archive into calibre": "Importar metadatos de Comic Rack del archivo de cómics a calibre",
    "Import Comment Metadata from the comic archive into calibre": "Importar metadatos de comentarios del archivo de cómics a calibre",
    "Embed both Comic Metadata types": "Incrustar ambos tipos de metadatos de cómic",
    "Only embed Metadata in zip comment": "Incrustar sólo metadatos en el comentario zip",
    "Only embed Metadata in ComicInfo.xml": "Solo incrustar metadatos en ComicInfo.xml",
    "Only convert to cbz": "Solo convertir a cbz",
    "Embed the calibre cover": "Incrustar la cubierta del calibre",
    "Count pages": "Contar páginas",
    'Remove metadata': 'Eliminar metadatos',
    "Get image size": "Obtener tamaño de imagen",
    # main button (ui.py)
    'Import Comic Metadata': 'Importar metadatos del cómic',
    'Imports the metadata from the comic to calibre': 'Importa los metadatos del cómic a calibre',
    'Embed Comic Metadata': 'Incrustar metadatos del cómic',
    'Embeds calibres metadata into the comic': 'Incrusta metadatos de calibre en el cómic',
    # config button (ui.py)
    "Configure": "Configurar",

    # COMPLETED MESSAGES (main.py)
    "Updated Calibre Metadata": "Metadatos de calibre actualizados",
    'Updated calibre metadata for {} book(s)': 'Metadatos de calibre actualizados para {} libro(s)',
    'The following books had no metadata: {}': 'Los siguientes libros no tenían metadatos: {}',
    "Updated comics": "Cómics actualizados",
    'Updated the metadata in the files of {} comics': 'Actualizados los metadatos en los archivos de {} comics',
    'The following books were not updated: {}': 'Los siguientes libros no fueron actualizados: {}',
    "Converted files": "Archivos convertidos",
    'Converted {} book(s) to cbz': 'Convertido {} libro(s) a cbz',
    'The following books were not converted: {}': 'Los siguientes libros no se convirtieron: {}',
    "Updated Covers": "Portadas Actualizadas",
    'Embeded {} covers': 'Portadas {} incrustadas',
    'The following covers were not embeded: {}': 'Las siguientes portadas no fueron incrustadas: {}',
    "Counted pages": "Páginas contadas",
    'Counted pages in {} comics': 'Páginas contadas en {} cómics',
    'The following comics were not counted: {}': 'No se contaron los siguientes cómics: {}',
    "The following comics were converted to cbz: {}": "Los siguientes cómics fueron convertidos a cbz: {}",
    'Removed metadata': 'Metadatos eliminados',
    'Removed metadata in {} comics': 'Se eliminaron metadatos en {} cómics',
    'The following comics did not have metadata removed: {}': 'A los siguientes cómics no se les eliminaron metadatos: {}',

    # ERRORS
    # (ui.py)
    'Cannot update metadata': 'No se pueden actualizar los metadatos',
    'No embed format selected': 'No se ha seleccionado ningún formato de inserción',
    # (main.py)
    'Cannot update metadata': 'No se pueden actualizar los metadatos',
    'No books selected': 'No hay libros seleccionados'
    # end
}
