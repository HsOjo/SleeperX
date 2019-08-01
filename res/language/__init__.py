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
    from .chinese import Chinese
    from .english import English

    LANGUAGES['en'] = English
    LANGUAGES['cn'] = Chinese

    language = LANGUAGES.get(code, English)()  # type: English
    return language
