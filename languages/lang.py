__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from calibre.utils.localization import get_lang
from .en import en
from .de import de


lang_dict = {
    "en": en,
    "de": de
}


lang = get_lang()
L = lang_dict.get(lang, lang_dict["en"])
