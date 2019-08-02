import os
import re

import common
from util import osa_api


def battery_status():
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
        common.log(battery_status, 'Warning', common.get_exception())
        return None


def set_sleep_available(b, **kwargs):
    osa_api.run_as_admin('/usr/bin/pmset -a disablesleep %d' % (0 if b else 1), **kwargs)


def sleep(display_only=False):
    os.system('/usr/bin/pmset %s' % ('displaysleepnow' if display_only else 'sleepnow'))


def sleep_info():
    p = common.popen('/usr/bin/pmset -g live')
    reg = re.compile('^\s+(?P<key>\S*)\s+(?P<value>\S*)\s*(?P<note>.*)$')
    lines = p.stdout.read().split('\n')
    items = {}
    notes = {}
    for line in lines:
        match = reg.match(line)
        if match is not None:
            item = match.groupdict()
            if 'key' in item and 'value' in item:
                v = item['value']
                if v.isnumeric():
                    v = int(v)
                elif v.replace('.', '', 1).isnumeric():
                    v = float(v)
                items[item['key']] = v
                if item['note'] != '':
                    notes[item['key']] = item['note']

    return items, notes


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
        p = common.popen('/usr/bin/pgrep %s|/usr/bin/xargs /bin/ps x -p' % name)
    else:
        p = common.popen('/bin/ps ax')
    lines = p.stdout.read().split('\n')[1:]

    items = []
    if len(lines) > 0:
        reg = re.compile('^(?P<PID>\S*)\s*(?P<TT>\S*)\s*(?P<STAT>\S*)\s*(?P<TIME>\S*)\s*(?P<COMMAND>.*)$')
        for i in lines:
            i = i.strip()
            if i != '':
                match = reg.match(i)
                if match is not None:
                    item = match.groupdict()
                    item['PID'] = int(item['PID'])
                    items.append(item)

    if pid is not None:
        if len(items) > 0:
            return items[0]
        else:
            return None
    else:
        return items


def check_lid():
    p = common.popen('/usr/sbin/ioreg -r -k AppleClamshellState')
    content = p.stdout.read()

    reg = re.compile(r'"AppleClamshellState" = (\S+)')
    result = common.reg_find_one(reg, content, None)

    if result == 'Yes':
        return True
    elif result == 'No':
        return False
    else:
        return None


def get_hid_idle_time():
    p = common.popen('/usr/sbin/ioreg -c IOHIDSystem')
    content = p.stdout.read()

    reg = re.compile(r'"HIDIdleTime" = (\d+)')
    times = [int(x) for x in reg.findall(content)]

    return max(times) / 1000000000
