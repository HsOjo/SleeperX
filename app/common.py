import json
import os
import sys
import time
import traceback
from io import StringIO
from subprocess import PIPE, Popen
from threading import Lock

io_log = StringIO()
io_err = StringIO()
lock_log = Lock()

to_json = lambda x: json.dumps(x, indent=4, ensure_ascii=False)
from_json = lambda x: json.loads(x)


# fix pyinstaller
def popen(cmd, sys_env=True, **kwargs):
    if sys_env and kwargs.get('env') is not None:
        kwargs['env'] = os.environ.copy().update(kwargs['env'])
    return Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8', **kwargs)


def execute(cmd, input=None, timeout=None, **kwargs):
    p = popen(cmd, **kwargs)
    if input is not None:
        p.stdin.write(input)
    out = p.stdout.read()
    err = p.stderr.read()
    stat = p.wait(timeout)
    return stat, out, err


def execute_get_out(cmd, **kwargs):
    [_, out, _] = execute(cmd, **kwargs)
    return out


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


def io_read_all(io: StringIO, default=None):
    if io is not None:
        io.seek(0)
        content = io.read()
        io.seek(0, 2)
    else:
        content = default
    return content


def extract_log():
    with lock_log:
        log = io_read_all(io_log, '')
    return log


def extract_err():
    err = io_read_all(io_err, '')
    return err


def log(src, tag='Info', *args):
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
        print('[%s] %s %s\n\t' % (tag, time.ctime(), source), *log_items)


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


def dict_to_object(d: dict, obj=object(), new_fields=True):
    for k, v in d.items():
        if new_fields or k in dir(obj):
            setattr(obj, k, v)


def get_runtime_dir():
    return getattr(sys, '_MEIPASS', '.')


def fix_encoding_in_pyinstaller():
    encoding = sys.getdefaultencoding()
    _init = Popen.__init__

    def init(*args, **kwargs):
        kwargs['encoding'] = kwargs.get('encoding', encoding)
        return _init(*args, **kwargs)

    Popen.__init__ = init

    __open = open

    def _open(*args, **kwargs):
        if len(args) >= 2:
            mode = args[1]
        else:
            mode = kwargs.get('mode')

        if isinstance(mode, str) and 'b' not in mode:
            kwargs['encoding'] = kwargs.get('encoding', encoding)
        return __open(*args, **kwargs)

    __builtins__['open'] = _open


def site_package_path():
    sp_paths = [x for x in sys.path if 'site-packages' in x]
    if len(sp_paths) > 0:
        sp_path = sp_paths[0]
    else:
        sp_path = None
    return sp_path


def runtime_path():
    paths = []
    for x in sys.path:
        path = '%s/../../bin/python' % x
        if 'python' in x and os.path.isdir(x) and os.path.exists(path):
            path = os.path.abspath(path)
            paths.append(path)

    if len(paths) > 0:
        return paths[0]

    return None
