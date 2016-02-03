__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'
from calibre.utils.localization import get_lang


L = get_translation()

lang_dict = {
    "en": en,
    "de": de
}


def get_translation():
    lang = get_lang()
    # l = lang_dict[lang]
    return lang_dict.get(lang, lang_dict["en"])
