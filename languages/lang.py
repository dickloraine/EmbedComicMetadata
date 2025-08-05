__license__   = 'GPL v3'
__copyright__ = '2015, dloraine'
__docformat__ = 'restructuredtext en'

from calibre.utils.localization import get_lang
from .en import en
from .es import es
from .de import de


lang_dict = {
    "en": en,
    "es": es,
    "de": de
}


lang = get_lang()
_L = lang_dict["en"]
if lang != "en" and lang in lang_dict:
    _L.update(lang_dict[lang])
