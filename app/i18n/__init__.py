from __future__ import annotations

LANGUAGES = {}


class Language:
    def unknown(self, key):
        return f'? ? ?: ({key})'

    def __getattr__(self, key):
        # Missing keys degrade to a visible placeholder instead of crashing.
        if key not in dir(self):
            return self.unknown(key)
        return None


def _register():
    from .english import English
    from .chinese import Chinese
    from .chinese_t import TraditionalChinese
    from .japanese import Japanese
    from .korean import Korean

    LANGUAGES.clear()
    LANGUAGES['en'] = English
    LANGUAGES['cn'] = Chinese
    LANGUAGES['cn_t'] = TraditionalChinese
    LANGUAGES['jp'] = Japanese
    LANGUAGES['ko'] = Korean


def load_language(code='en'):
    if not LANGUAGES:
        _register()
    from .english import English
    return LANGUAGES.get(code, English)()


def map_locale(locale_code: str) -> str:
    """Map an NSLocale-style identifier to one of our 5 supported codes."""
    if not locale_code:
        return 'en'
    c = locale_code.replace('_', '-').lower()
    if c.startswith('zh'):
        if 'hant' in c or 'tw' in c or 'hk' in c or 'mo' in c:
            return 'cn_t'
        return 'cn'
    if c.startswith('ja'):
        return 'jp'
    if c.startswith('ko'):
        return 'ko'
    return 'en'


def format_countdown(seconds) -> str:
    """Format a countdown as HH:MM:SS or MM:SS, precise to the second."""
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f'{hours}:{minutes:02d}:{secs:02d}'
    return f'{minutes}:{secs:02d}'


def format_duration(lang, seconds) -> str:
    """Format a duration in seconds using the language's time-unit strings."""
    total = int(seconds)
    day, total = divmod(total, 86400)
    hour, total = divmod(total, 3600)
    minute, second = divmod(total, 60)
    result = ''
    if day > 0:
        result += f'{day}{lang.time_days}'
    if hour > 0:
        result += f'{hour}{lang.time_hours}'
    if minute > 0:
        result += f'{minute}{lang.time_minutes}'
    if second > 0 or result == '':
        result += f'{second}{lang.time_seconds}'
    return result
