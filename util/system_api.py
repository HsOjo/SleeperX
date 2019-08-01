import os
import re

import common
from util import osa_api


def battery_info():
    try:
        p = common.popen('/usr/bin/pmset -g ps')
        msg = p.stdout.read()

        reg = re.compile('(\d*%); (.*?); (.*?) present: ')
        [res] = reg.findall(msg.replace('AC attached; not charging', 'not charging; (no estimate)'))

        remaining = res[2].replace(' remaining', '')
        remaining = common.convert_minute(remaining) if remaining != '(no estimate)' else None

        info = {
            'percent': int(res[0][:-1]),
            'status': res[1],
            'remaining': remaining,
        }

        return info
    except:
        common.log(battery_info, 'Warning', common.get_exception())
        return None


def sleep(**kwargs):
    osa_api.run_as_admin('/usr/bin/pmset sleepnow', **kwargs)


def sleep_info():
    p = common.popen('/usr/bin/pmset -g')
    data = p.stdout.read()
    data = data[data.find('\n '):].split('\n')
    res = {}
    for row in data:
        row = row.strip()
        if row != '':
            p_row = ''
            while p_row != row:
                p_row = row
                row = row.replace('  ', ' ')
            cols = row.split(' ')
            if len(cols) >= 2:
                k = cols[0]
                v = cols[1]
                if v.isnumeric():
                    v = int(v)
                elif v.replace('.', '').isnumeric():
                    v = float(v)
                res[k] = v

    return res


def set_sleep_mode(mode, **kwargs):
    if mode in [0, 3, 25]:
        osa_api.run_as_admin('/usr/bin/pmset hibernatemode %d' % mode, **kwargs)


def open_url(url, new=False):
    param = ' -n' if new else ''
    os.system('/usr/bin/open%s "%s"' % (param, url))


def check_process(pid: int = None, name=None):
    if pid is not None:
        p = common.popen('/bin/ps %d' % pid)
    elif name is not None:
        p = common.popen('/usr/bin/pgrep %s|xargs /bin/ps x -p' % name)
    else:
        p = common.popen('/bin/ps ax')
    lines = p.stdout.read().split('\n')[1:]

    items = []
    if len(lines) > 0:
        reg = re.compile('^(?P<PID>\S*)\s*(?P<TT>\S*)\s*(?P<STAT>\S*)\s*(?P<TIME>\S*)\s*(?P<COMMAND>.*)$')
        for i in lines:
            i = i.strip()
            if i != '':
                item = reg.match(i).groupdict()
                item['PID'] = int(item['PID'])
                items.append(item)

    if pid is not None:
        if len(items) > 0:
            return items[0]
        else:
            return None
    else:
        return items
