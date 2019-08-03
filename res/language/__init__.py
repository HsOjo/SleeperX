LANGUAGES = {}


class Language:
    unknown = '? ? ?: (%s)'

    def __getattr__(self, key):
        if key not in dir(self):
            if '%s' in self.unknown:
                return self.unknown % key
            else:
                return self.unknown


def load_language(code):
    from .english import English
    from .chinese import Chinese
    from .chinese_t import TraditionalChinese

    LANGUAGES['en'] = English
    LANGUAGES['cn'] = Chinese
    LANGUAGES['cn_t'] = TraditionalChinese

    language = LANGUAGES.get(code, English)()  # type: English
    return language
