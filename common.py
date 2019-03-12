import os
import subprocess
import sys
import traceback
from io import StringIO

io_log = StringIO()


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
