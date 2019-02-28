import os
import re
import subprocess
import traceback
from io import StringIO


def popen(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')


def osascript_run(applescript: str):
    try:
        p = popen('/usr/bin/osascript -e "%s"' % applescript.replace('"', '\\"'))
        out = p.stdout.read()
        err = p.stderr.read()
        return p.wait(), out, err
    except:
        with StringIO() as io:
            traceback.print_exc(file=io)
            io.seek(0)
            err = io.read()

        return -1, '', err


def convert_minute(t):
    h, m = list(map(int, t.split(':')))
    return h * 60 + m


def battery_info():
    msg = os.popen('pmset -g ps').read()

    reg = re.compile('(\d*%); (.*?); (.*?) present: ')
    [res] = reg.findall(msg.replace('AC attached; not charging', 'not charging; (no estimate)'))

    remaining = res[2].replace(' remaining', '')
    remaining = convert_minute(remaining) if remaining != '(no estimate)' else None

    info = {
        'percent': int(res[0][:-1]),
        'status': res[1],
        'remaining': remaining,
    }

    return info


def run_as_admin(cmd, pwd, user=''):
    cmd = cmd.replace('"', '\\"')
    user = user.replace('"', '\\"')
    pwd = pwd.replace('"', '\\"')

    [stat, out, err] = osascript_run(
        'do shell script "%s" %spassword "%s" with administrator privileges' % (
            cmd, (('user name "%s" ' % user) if user != '' else ''), pwd))
    return stat, out, err


def sleep(**kwargs):
    run_as_admin('shutdown -s now', **kwargs)


def gui_input(title, description, default='', hidden=False):
    title = title.replace('"', '\\"')
    description = description.replace('"', '\\"')
    default = default.replace('"', '\\"')

    [stat, out, err] = osascript_run(
        'display dialog "%s" with title "%s" default answer "%s" hidden answer %s' %
        (description, title, default, hidden))

    content = None
    if out != '':
        reg = re.compile('text returned:(.*)')
        [content] = reg.findall(out)

    return content
