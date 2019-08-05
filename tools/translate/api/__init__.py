import json
import os

from app import common
from .baidu import BaiduTranslate
from .google import GoogleTranslate
from .translator import Translator
from .zhconv import ZHConv

CONFIG_FILE = '%s/tools/translate/config.json' % common.get_runtime_dir()

config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as io:
        config = json.load(io)


def baidu_translate():
    return BaiduTranslate(**config.get('baidu'))


def google_translate():
    return GoogleTranslate()


def zhconv():
    return ZHConv()
