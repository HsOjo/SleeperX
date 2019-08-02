import json
import os
import sys
import time
import traceback
from io import StringIO
from subprocess import PIPE, Popen
from threading import Lock

io_log = StringIO()
lock_log = Lock()


def popen(cmd):
    return Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf8')


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
    else:
        log = ''
    return log


def log(src, tag='Info', *args):
    to_json = lambda x: json.dumps(x, indent=4, ensure_ascii=False)

    log_items = []
    for i in args:
        if isinstance(i, list) or isinstance(i, dict):
            log_items.append(to_json(i))
        elif isinstance(i, tuple) or isinstance(i, set):
            log_items.append(to_json(list(i)))
        elif isinstance(i, int) or isinstance(i, float) or isinstance(i, str) or isinstance(i, bool) or i is None:
            log_items.append(i)
        else:
            log_items.append(i)
            log_items.append(to_json(object_to_dict(i)))

    if isinstance(src, str):
        source = src
    else:
        source = src.__name__

    with lock_log:
        print('[%s] %s\n%s' % (tag, time.ctime(), source), *log_items)


def wait_and_check(wait: float, step: float):
    def core(func):
        def _core(*args, **kwargs):
            for i in range(int(wait // step)):
                if not func(*args, **kwargs):
                    return False
                time.sleep(step)
            time.sleep(wait % step)
            return True

        return _core

    return core


def time_count(func):
    def core(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        print('%s time usage: %f' % (func.__name__, time.time() - t))
        return result

    return core


def object_to_dict(obj):
    r = {}
    for k in dir(obj):
        if k[0] != '_':
            v = getattr(obj, k)
            if not callable(v):
                r[k] = v

    return r


def dict_to_obj(d: dict, obj=object(), new_fields=True):
    for k, v in d.items():
        if new_fields or hasattr(obj, k):
            setattr(obj, k, v)


def get_resource_dir():
    return getattr(sys, '_MEIPASS', '.')
