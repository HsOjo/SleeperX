import json
import os

import common
from .baidu_translate import BaiduTranslate
from .google_translate import GoogleTranslate

CONFIG_FILE = '%s/tools/translate/config.json' % common.get_runtime_dir()

config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as io:
        config = json.load(io)


def baidu_translate():
    bt = BaiduTranslate(**config.get('baidu'))
    return bt


def google_translate():
    gt = GoogleTranslate()
    return gt
