from zhconv import convert

from .chinese import Chinese


class TraditionalChinese(Chinese):
    l_this = convert('繁体中文', 'zh-hant')

    def __init__(self):
        replace = {
            '文件': '档案',
            '设置': '设定',
            '显示器': '显示幕',
            '磁盘': '磁碟',
            '内存': '记忆体',
            '模式': '范式',
        }

        for k in dir(self):
            if k[0] != '_':
                v = getattr(self, k)
                if isinstance(v, str):
                    for i, c in replace.items():
                        v = v.replace(i, c)
                    setattr(self, k, convert(v, 'zh-hant'))
