import re

from app import common
from app.util.log import Log


def battery_status():
    def convert_second(t):
        h, m = list(map(int, t.split(':')))
        return (h * 60 + m) * 60

    try:
        content = common.execute_get_out(['/usr/bin/pmset', '-g', 'ps'])

        reg = re.compile(r'(\d*%); (.*?); (.*?) present: ')
        [res] = reg.findall(content.replace('AC attached; not charging', 'not charging; (no estimate)'))

        remaining = res[2].replace(' remaining', '')
        remaining = convert_second(remaining) if remaining != '(no estimate)' else None

        info = {
            'percent': int(res[0][:-1]),
            'status': res[1],
            'remaining': remaining,
        }

        return info
    except:
        Log.append(battery_status, 'Warning', common.get_exception())
        return None


def set_sleep_available(available, ex_func):
    return ex_func('/usr/bin/pmset -a disablesleep %d' % (0 if available else 1))


def sleep(display_only=False):
    return common.execute(['/usr/bin/pmset', 'displaysleepnow' if display_only else 'sleepnow'])


def sleep_info():
    content = common.execute_get_out(['/usr/bin/pmset', '-g', 'live'])
    reg = re.compile(r'^\s+(?P<key>\S*)\s+(?P<value>\S*)\s*(?P<note>.*)$')

    lines = content.split('\n')
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


def set_sleep_mode(mode, ex_func):
    if mode in [0, 3, 25]:
        return ex_func('/usr/bin/pmset hibernatemode %d' % mode)


def open_url(url, new=False, wait=False, bundle: str = None, p_args=None):
    args = ['/usr/bin/open']
    if new:
        args.append('-n')
    if wait:
        args.append('-W')
    if bundle:
        args.append('-b')
        args.append(bundle)

    args.append(url)

    if p_args is not None:
        args.append('--args')
        for arg in p_args:
            args.append(arg)

    return common.execute(args)


def check_process(pid: int = None, name=None):
    if pid is not None:
        content = common.execute_get_out(['/bin/ps', str(pid)])
    elif name is not None:
        content = common.execute_get_out('/usr/bin/pgrep %s|/usr/bin/xargs /bin/ps x -p' % name, shell=True)
    else:
        content = common.execute_get_out(['/bin/ps', 'ax'])
    lines = content.split('\n')[1:]

    items = []
    if len(lines) > 0:
        reg = re.compile(r'^(?P<PID>\S*)\s*(?P<TT>\S*)\s*(?P<STAT>\S*)\s*(?P<TIME>\S*)\s*(?P<COMMAND>.*)$')
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
    content = common.execute_get_out(['/usr/sbin/ioreg', '-c', 'IOPMrootDomain', '-d', '4'])

    reg = re.compile(r'"AppleClamshellState" = (\S+)')
    result = common.reg_find_one(reg, content, None)

    if result == 'Yes':
        return True
    elif result == 'No':
        return False
    else:
        return None


def get_hid_idle_time():
    content = common.execute_get_out(['/usr/sbin/ioreg', '-c', 'IOHIDSystem', '-d', '4'])

    reg = re.compile(r'"HIDIdleTime" = (\d+)')
    result = common.reg_find_one(reg, content, None)

    return int(result) / 1000000000


def check_admin(username=None):
    args = ['/usr/bin/groups']
    if username is not None:
        args.append(username)

    content = common.execute_get_out(args)
    groups = content.split(' ')

    return 'admin' in groups


def sudo(command: str, password: str, timeout=None):
    stat, out, err = common.execute('/usr/bin/sudo -S %s' % (command), '%s\n' % password, timeout, shell=True)
    Log.append(sudo, 'sudo', locals())
    return stat, out, err


def get_system_version():
    content = common.execute_get_out(['/usr/sbin/system_profiler', 'SPSoftwareDataType'])
    result = {}
    reg = re.compile('(.*): (.*)')
    for item in reg.findall(content):
        result[item[0].strip()] = item[1].strip()
    return result
