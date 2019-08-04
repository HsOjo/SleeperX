import json
import os

import common
from .english import English


class TranslateLanguage(English):
    _resource_name = ''
    _translate_by = English
    _translate_from = 'en'
    _translate_to = ''
    _replace_words = {}

    def __init__(self):
        self._data_path = '%s/res/language/translate/%s.json' % (
            common.get_runtime_dir(), self._resource_name[self._resource_name.rfind('.') + 1:])

        translate = True
        if os.path.exists(self._data_path):
            try:
                with open(self._data_path, 'r') as io:
                    language = json.load(io)
                common.dict_to_object(language, self, False)
                translate = False
            except:
                pass

        if translate:
            self.online_translate()
            language = common.object_to_dict(self)
            with open(self._data_path, 'w') as io:
                json.dump(language, io, ensure_ascii=False, indent=4)

    def online_translate(self):
        def replace(text):
            for i, c in self._replace_words.items():
                text = text.replace(i, c)
            return text

        from tools.translate.api.google_translate import GoogleTranlate
        gt = GoogleTranlate()

        def translate(text):
            _text = text
            text = replace(text)
            text = gt.translate(text, self._translate_from, self._translate_to)
            text = replace(text)
            common.log(self.online_translate, 'Translate', '\n%s\n%s' % (_text, text))
            return text

        for k in dir(self._translate_by):
            if k[0] != '_' and k != 'l_this':
                v = getattr(self._translate_by, k)
                if isinstance(v, str):
                    setattr(self, k, translate(v))
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        v[kk] = translate(vv)
                    setattr(self, k, v)
