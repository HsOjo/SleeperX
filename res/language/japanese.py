from .chinese import Chinese
from .translate_language import TranslateLanguage


class Japanese(TranslateLanguage):
    _resource_name = __name__
    _translate_by = Chinese
    _translate_from = 'cn'
    _translate_to = 'jp'
    _replace_words = {
        '％': '%'
    }

    l_this = '日本語'
