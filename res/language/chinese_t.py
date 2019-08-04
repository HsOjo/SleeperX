from zhconv import convert

from .chinese import Chinese


class TraditionalChinese(Chinese):
    l_this = convert('繁体中文', 'zh-hant')
    _replace_words = {
        '文件': '档案',
        '设置': '设定',
        '显示器': '显示幕',
        '磁盘': '磁碟',
        '内存': '记忆体',
        '模式': '范式',
    }

    def __init__(self):
        def replace(text):
            for i, c in self._replace_words.items():
                text = text.replace(i, c)
            return text

        def translate(text):
            text = replace(text)
            text = convert(text, 'zh-hant')
            text = replace(text)
            return text

        for k in dir(self):
            if k[0] != '_':
                v = getattr(self, k)
                if isinstance(v, str):
                    setattr(self, k, translate(v))
                elif isinstance(v, dict):
                    v = v.copy()
                    for kk, vv in v.items():
                        v[kk] = translate(vv)
                    setattr(self, k, v)
