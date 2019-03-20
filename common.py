import json
import os
import subprocess
import sys
import traceback
from io import StringIO
from threading import Lock

io_log = StringIO()
lock_log = Lock()


def popen(cmd):
    return subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding='utf8')


def convert_minute(t):
    h, m = list(map(int, t.split(':')))
    return h * 60 + m


def get_exception():
    with StringIO() as io:
        traceback.print_exc(file=io)
        io.seek(0)
        content = io.read()

    return content


def reg_find_one(reg, content, default=''):
    res = reg.findall(content)
    if len(res) > 0:
        return res[0]
    else:
        return default


def get_application_info():
    name = None
    path = None
    if getattr(sys, 'frozen', False):
        name = os.path.basename(sys.executable)
        path = os.path.abspath('%s/../../..' % sys.executable)

    return name, path


def compare_version(a: str, b: str, ex=False):
    sa = a.split('-')
    sb = b.split('-')

    if ex is False and len(sb) > 1:
        return False
    else:
        return int(sa[0].replace('.', '')) < int(sb[0].replace('.', ''))


def extract_log():
    if isinstance(io_log, StringIO):
        io_log.seek(0)
        log = io_log.read()
        io_log.seek(0, 2)
    return log


def log(src, tag='Info', *args):
    log_items = []
    for i in args:
        if isinstance(i, list) or isinstance(i, dict):
            log_items.append(json.dumps(i, indent=4, ensure_ascii=False))
        elif isinstance(i, tuple):
            log_items.append(json.dumps(list(i), indent=4, ensure_ascii=False))
        else:
            log_items.append(i)

    if isinstance(src, str):
        source = src
    else:
        source = src.__name__

    with lock_log:
        print('[%s] %s' % (tag, source), *log_items)
